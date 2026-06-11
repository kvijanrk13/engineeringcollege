from pypdf import PdfMerger
from PIL import Image
import tempfile
import os
import requests

def merge_files(file_list):
    merger = PdfMerger()
    temp_files = []

    for file in file_list:
        if not file:
            continue

        try:
            file_url = file.url if hasattr(file, "url") else file

            # Download file if it's a URL (Cloudinary case)
            if isinstance(file_url, str) and file_url.startswith("http"):
                response = requests.get(file_url)
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(response.content)
                temp.close()
                file_path = temp.name
            else:
                file_path = file.path

            # IMAGE → convert to PDF
            if file_url.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(file_path)
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                img.convert('RGB').save(temp_pdf.name)
                merger.append(temp_pdf.name)
                temp_files.append(temp_pdf.name)

            # PDF → directly append
            elif file_url.lower().endswith('.pdf'):
                merger.append(file_path)

        except Exception as e:
            print("Error processing file:", e)

    # Final merged PDF
    final_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(final_pdf.name)
    merger.close()

    # Cleanup temp files
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass

    return final_pdf.name