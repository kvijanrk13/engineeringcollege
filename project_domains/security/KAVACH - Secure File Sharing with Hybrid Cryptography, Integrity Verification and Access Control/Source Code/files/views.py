from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from urllib.parse import quote

from .crypto import decrypt_file_bytes, encrypt_file_bytes
from .forms import PlainTextFileUploadForm
from .models import PlainTextFile


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

            encrypted_name = f"{uploaded_file.name}.aesgcm"
            plain_text_file = PlainTextFile(
                owner=request.user,
                receiver_email=form.cleaned_data["receiver_email"],
                original_name=uploaded_file.name,
                file_size=uploaded_file.size,
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
                f"Text file encrypted with AES-GCM and shared with {plain_text_file.receiver_email}.",
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
    received_file.uploaded_file.open("rb")
    try:
        decrypted_bytes = decrypt_file_bytes(
            received_file.uploaded_file.read(),
            received_file.aes_key,
            received_file.aes_nonce,
        )
    finally:
        received_file.uploaded_file.close()

    response = HttpResponse(decrypted_bytes, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(received_file.original_name)}"
    return response
