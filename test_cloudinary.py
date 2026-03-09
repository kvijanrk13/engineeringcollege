# test_cloudinary.py
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dsndirhuhe')
api_key = os.environ.get('CLOUDINARY_API_KEY', '473455725389669')
api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'vztmkO4bDwTVvVNG7Mah9yPmkdY')

print("=" * 60)
print("CLOUDINARY CONNECTION TEST")
print("=" * 60)
print(f"Cloud Name: {cloud_name}")
print(f"API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else api_key}")
print(f"API Secret: {'*' * 8}{api_secret[-4:] if len(api_secret) > 4 else ''}")
print("-" * 60)

# Configure Cloudinary
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)

try:
    # Test 1: Ping the API
    print("Test 1: Pinging Cloudinary API...")
    result = cloudinary.api.ping()
    print(f"✓ Ping successful: {result}")

    # Test 2: Get account usage
    print("\nTest 2: Getting account usage...")
    usage = cloudinary.api.usage()
    print(f"✓ Usage retrieved successfully")
    print(f"  - Plan: {usage.get('plan', 'N/A')}")
    print(f"  - Credits used: {usage.get('credits', {}).get('usage', 'N/A')}")

    print("\n✅ Cloudinary connection successful!")

except Exception as e:
    print(f"\n❌ Cloudinary connection failed: {e}")

    # Provide helpful suggestions
    print("\nPossible solutions:")
    print("1. Verify your cloud name at https://cloudinary.com")
    print("2. Check if your account is active")
    print("3. Ensure your API key and secret are correct")
    print("4. Try creating a new API key in your Cloudinary dashboard")