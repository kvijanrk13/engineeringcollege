# dashboard/utils/qr_utils.py
import qrcode
from io import BytesIO
import base64
from django.core.files.base import ContentFile


def generate_qr_code(data, size=10, border=4):
    """Generate QR code image"""
    try:
        qr = qrcode.QRCode(
            version=1,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def generate_qr_code_base64(data, size=10):
    """Generate QR code and return as base64 string"""
    buffer = generate_qr_code(data, size)
    if buffer:
        return base64.b64encode(buffer.getvalue()).decode()
    return None


def generate_qr_code_file(data, filename=None):
    """Generate QR code and return as Django ContentFile"""
    import hashlib
    buffer = generate_qr_code(data)
    if buffer:
        if not filename:
            filename = f"qr_{hashlib.md5(data.encode()).hexdigest()[:10]}.png"
        return ContentFile(buffer.getvalue(), name=filename)
    return None