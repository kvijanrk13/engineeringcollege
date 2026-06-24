import hashlib
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .crypto import decrypt_file_bytes, encrypt_file_bytes
from .forms import PlainTextFileUploadForm
from .models import PlainTextFile


def file_sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


def decrypt_and_verify_file(shared_file):
    shared_file.uploaded_file.open("rb")
    try:
        decrypted_bytes = decrypt_file_bytes(
            shared_file.uploaded_file.read(),
            shared_file.aes_key,
            shared_file.aes_nonce,
        )
    finally:
        shared_file.uploaded_file.close()

    decrypted_hash = file_sha256(decrypted_bytes)
    return decrypted_bytes, decrypted_hash, bool(shared_file.sha256_hash and decrypted_hash == shared_file.sha256_hash)


@login_required
def my_files_view(request):
    sent_files = PlainTextFile.objects.filter(owner=request.user)
    received_files = PlainTextFile.objects.filter(receiver_email=(request.user.email or "").lower())
    return render(
        request,
        "files/my_files.html",
        {"sent_files": sent_files, "received_files": received_files},
    )


@login_required
def upload_file_view(request):
    if request.method == "POST":
        form = PlainTextFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["uploaded_file"]
            file_bytes = uploaded_file.read()
            encrypted_payload = encrypt_file_bytes(file_bytes)
            original_hash = file_sha256(file_bytes)

            encrypted_name = f"{uploaded_file.name}.aesgcm"
            plain_text_file = PlainTextFile(
                owner=request.user,
                receiver_email=form.cleaned_data["receiver_email"],
                original_name=uploaded_file.name,
                file_size=uploaded_file.size,
                sha256_hash=original_hash,
                aes_key=encrypted_payload.aes_key,
                aes_nonce=encrypted_payload.nonce,
            )
            plain_text_file.uploaded_file.save(
                encrypted_name,
                ContentFile(encrypted_payload.ciphertext),
                save=False,
            )
            plain_text_file.save()

            messages.success(
                request,
                f"Text file encrypted with AES-GCM and SHA-256 verified fingerprint stored for {plain_text_file.receiver_email}.",
            )
            return redirect("files:my_files")
    else:
        form = PlainTextFileUploadForm()

    return render(request, "files/upload.html", {"form": form})


@login_required
def download_file_view(request, file_id):
    received_file = get_object_or_404(
        PlainTextFile,
        id=file_id,
        receiver_email=(request.user.email or "").lower(),
    )
    decrypted_bytes, _decrypted_hash, is_safe = decrypt_and_verify_file(received_file)
    if not is_safe:
        messages.error(request, "Integrity verification failed. The decrypted file fingerprint does not match the stored SHA-256 hash.")
        return redirect("accounts:profile")

    response = HttpResponse(decrypted_bytes, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(received_file.original_name)}"
    return response
