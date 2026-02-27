# check_cloudinary.py
import os
import django
import cloudinary
import cloudinary.api

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Certificate


def check_cloudinary_certificates():
    print("Checking Cloudinary certificates...")

    certificates = Certificate.objects.exclude(cloudinary_url__isnull=True).exclude(cloudinary_url='')

    if not certificates.exists():
        print("No certificates with Cloudinary URLs found")
        return

    for cert in certificates:
        print(f"\nCertificate {cert.id}:")
        print(f"  Type: {cert.certificate_type}")
        print(f"  Faculty: {cert.faculty.staff_name}")
        print(f"  Cloudinary URL: {cert.cloudinary_url}")

        # Test the URL
        try:
            import requests
            response = requests.head(cert.cloudinary_url, timeout=10)
            if response.status_code == 200:
                print(f"  ✓ URL is accessible")
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' in content_type.lower():
                    print(f"  ✓ Is a PDF file")
                else:
                    print(f"  ⚠ Not a PDF: {content_type}")
            else:
                print(f"  ✗ URL returned status {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error checking URL: {e}")


if __name__ == "__main__":
    check_cloudinary_certificates()