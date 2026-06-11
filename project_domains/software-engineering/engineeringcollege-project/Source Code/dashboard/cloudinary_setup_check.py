# test_cloudinary_setup.py
import sys

print(f"Python: {sys.version}\n")

# Test imports
try:
    import six

    print("✓ six imported")
except ImportError:
    print("✗ six NOT imported")

try:
    import cloudinary

    print(f"✓ cloudinary imported (v{cloudinary.__version__})")
except ImportError as e:
    print(f"✗ cloudinary NOT imported: {e}")

try:
    import cloudinary_storage

    print("✓ cloudinary_storage imported")
except ImportError as e:
    print(f"✗ cloudinary_storage NOT imported: {e}")

print("\nTesting Cloudinary configuration...")
try:
    cloudinary.config(
        cloud_name='dsndiruhe',
        api_key='796293117737693',
        api_secret='StgoTNd4fgLqHqW19csQ4fONAuk',
        secure=True
    )
    print("✓ Cloudinary configured")

    # Test signed URL generation
    import cloudinary.utils

    test_url = "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125044/certificates/uo1jjxppjtfkuvzu6aro.pdf"
    import re

    match = re.search(r'upload/(v\d+)/(.*?\.pdf)', test_url)
    if match:
        public_id = match.group(2).replace('.pdf', '')
        version = match.group(1)
        signed_url = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type='raw',
            version=version,
            secure=True,
            sign_url=True
        )[0]
        print(f"✓ Signed URL generated: {signed_url[:80]}...")

except Exception as e:
    print(f"✗ Cloudinary configuration failed: {e}")

print("\n✅ Test complete!")