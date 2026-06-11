# quick_debug.py
import cloudinary.utils
import re

# Simple test to see if signed URL generation works
test_url = "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125044/certificates/uo1jjxppjtfkuvzu6aro.pdf"

print("Testing Signed URL Generation...")
print(f"Original URL: {test_url}")

# Extract public_id
pattern = r'upload/(v\d+)/(.*?\.pdf)'
match = re.search(pattern, test_url)

if match:
    version = match.group(1)
    public_id_with_ext = match.group(2)
    public_id = public_id_with_ext.replace('.pdf', '')

    print(f"\nExtracted:")
    print(f"  Version: {version}")
    print(f"  Public ID: {public_id}")

    try:
        # Generate signed URL
        signed_url, options = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type='raw',
            version=version,
            secure=True,
            sign_url=True
        )
        print(f"\nGenerated Signed URL:")
        print(f"  {signed_url}")
        print(f"\n✓ Signed URL generation successful!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
else:
    print("✗ Could not parse URL")