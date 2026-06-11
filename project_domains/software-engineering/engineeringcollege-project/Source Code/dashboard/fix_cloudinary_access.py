# fix_cloudinary_access.py
import cloudinary
import cloudinary.api
import sys
import os

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Cloudinary - Get these from Cloudinary Dashboard
cloudinary.config(
    cloud_name='dsndiruhe',
    api_key='796293117737693',  # Replace with your API Key
    api_secret='StgoTNd4fgLqHqW19csQ4fONAuk'  # Replace with your API Secret
)


def make_certificates_public():
    """Make all PDFs in certificates folder public"""
    try:
        # List all resources in certificates folder
        resources = cloudinary.api.resources(
            type='upload',
            prefix='certificates/',
            resource_type='raw',
            max_results=100
        )

        print(f"Found {len(resources.get('resources', []))} resources")

        # Update each resource to be public
        for resource in resources.get('resources', []):
            public_id = resource['public_id']
            resource_type = resource['resource_type']

            print(f"Updating: {public_id}")

            # Update to public access
            result = cloudinary.api.update(
                public_id,
                resource_type=resource_type,
                access_mode='public'
            )
            print(f"✓ Made public: {public_id}")

    except Exception as e:
        print(f"Error: {e}")


def test_access():
    """Test if certificates are now accessible"""
    import requests
    test_urls = [
        "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125044/certificates/uo1jjxppjtfkuvzu6aro.pdf",
        "https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125045/certificates/q8dmr0im4c4jlu1qzuyr.pdf"
    ]

    for url in test_urls:
        try:
            response = requests.head(url)  # Use HEAD to check without downloading
            print(f"URL: {url}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Accessible")
            else:
                print("✗ Still not accessible")
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Step 1: Making certificates public...")
    make_certificates_public()

    print("\nStep 2: Testing access...")
    test_access()