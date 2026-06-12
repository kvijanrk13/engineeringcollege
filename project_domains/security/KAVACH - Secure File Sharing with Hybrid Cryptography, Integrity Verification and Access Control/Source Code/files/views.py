from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

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
            preview_bytes = uploaded_file.read(2000)
            uploaded_file.seek(0)
            preview_text = preview_bytes.decode("utf-8", errors="replace")

            plain_text_file = form.save(commit=False)
            plain_text_file.owner = request.user
            plain_text_file.original_name = uploaded_file.name
            plain_text_file.file_size = uploaded_file.size
            plain_text_file.preview_text = preview_text
            plain_text_file.save()

            messages.success(request, "Text file uploaded successfully and prepared for encryption.")
            return redirect("files:my_files")
    else:
        form = PlainTextFileUploadForm()

    return render(request, "files/upload.html", {"form": form})
