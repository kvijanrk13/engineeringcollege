from pathlib import Path

from django import forms

from .models import PlainTextFile


class PlainTextFileUploadForm(forms.ModelForm):
    class Meta:
        model = PlainTextFile
        fields = ("uploaded_file",)
        labels = {
            "uploaded_file": "Select file to encrypt",
        }
        help_texts = {
            "uploaded_file": "Only .txt files are accepted. AES is used because it is fast for large files.",
        }

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data["uploaded_file"]
        extension = Path(uploaded_file.name).suffix.lower()
        if extension != ".txt":
            raise forms.ValidationError("Please upload only Notepad text files with .txt extension.")
        if uploaded_file.size > 1024 * 1024:
            raise forms.ValidationError("Please upload a text file smaller than 1 MB for this beginner step.")
        return uploaded_file
