from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render

from .crypto import encrypt_file_bytes
from .forms import PlainTextFileUploadForm
from .models import PlainTextFile


@login_required
def my_files_view(request):
    files = PlainTextFile.objects.filter(owner=request.user)
    return render(request, "files/my_files.html", {"files": files})


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

            messages.success(request, "Text file encrypted with AES-GCM and uploaded successfully.")
            return redirect("files:my_files")
    else:
        form = PlainTextFileUploadForm()

    return render(request, "files/upload.html", {"form": form})
