# test_cloudinary_auth.py
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

import cloudinary
import requests
from dashboard.utils.cloudinary_utils import get_signed_pdf_url, download_certificate_with_auth

# Test URLs from your logs
test_urls = [
    "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125044/certificates/uo1jjxppjtfkuvzu6aro.pdf",
    "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125045/certificates/q8dmr0im4c4jlu1qzuyr.pdf"
]

print("Testing Cloudinary Authentication Setup...")
print("=" * 70)

# Test 1: Direct access (should fail with 401)
print("\n1. Testing Direct Access (Expected: 401):")
for url in test_urls:
    response = requests.get(url)
    print(f"  {url}")
    print(f"  Status: {response.status_code} (Expected: 401)")
    print()

# Test 2: Signed URL access
print("2. Testing Signed URL Access (Expected: 200):")
for url in test_urls:
    signed_url = get_signed_pdf_url(url)
    print(f"  Original: {url}")
    print(f"  Signed: {signed_url}")

    response = requests.get(signed_url)
    if response.status_code == 200:
        print(f"  ✓ SUCCESS - Status: {response.status_code}, Size: {len(response.content)} bytes")
    else:
        print(f"  ✗ FAILED - Status: {response.status_code}")
    print()

# Test 3: Using the utility function
print("3. Testing Utility Function:")
for url in test_urls:
    print(f"  Testing: {url}")
    content = download_certificate_with_auth(url)
    if content:
        print(f"  ✓ SUCCESS - Downloaded {len(content.getvalue())} bytes")
    else:
        print(f"  ✗ FAILED - No content")
    print()

print("=" * 70)
print("Test Complete!")