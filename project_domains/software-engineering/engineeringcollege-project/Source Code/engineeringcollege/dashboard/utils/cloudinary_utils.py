# dashboard/utils/cloudinary_utils.py
import cloudinary.api
import cloudinary.utils
import re
import requests
from io import BytesIO
import traceback

def extract_public_id_from_url(url):
    """
    Extract public_id from Cloudinary URL
    Example: https://res.cloudinary.com/dsndiruhe/raw/upload/v1768125044/certificates/uo1jjxppjtfkuvzu6aro.pdf
    Returns: certificates/uo1jjxppjtfkuvzu6aro
    """
    try:
        # Pattern to match Cloudinary URLs
        pattern = r'upload/(v\d+/)?(.*?)(?:\.(pdf|jpg|jpeg|png))?$'
        match = re.search(pattern, url, re.IGNORECASE)

        if match:
            public_id = match.group(2)
            return public_id

        return None
    except Exception as e:
        print(f"Error extracting public_id: {e}")
        return None

def get_cloudinary_resource(public_id, resource_type='raw'):
    """
    Get Cloudinary resource info using API with authentication.
    """
    try:
        resource = cloudinary.api.resource(public_id, resource_type=resource_type)
        return resource
    except Exception as e:
        print(f"Error getting Cloudinary resource: {e}")
        return None

def download_certificate_with_auth(url):
    """
    Download certificate from Cloudinary with proper authentication.
    Uses Cloudinary API to get authenticated URL.
    """
    try:
        print(f"Attempting to download with authentication: {url}")

        # Get signed URL if it's a Cloudinary URL
        if 'cloudinary.com' in url:
            # Extract public_id from URL
            public_id = extract_public_id_from_url(url)
            if public_id:
                print(f"Extracted public_id: {public_id}")

                # Try different resource types
                for res_type in ['raw', 'image', 'auto']:
                    try:
                        # Get resource info from Cloudinary API
                        resource = get_cloudinary_resource(public_id, resource_type=res_type)
                        if resource and 'secure_url' in resource:
                            download_url = resource['secure_url']
                            print(f"Using Cloudinary API URL ({res_type}): {download_url}")

                            # Download with proper headers
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            }
                            response = requests.get(download_url, headers=headers, timeout=30)
                            print(f"Download status for {download_url}: {response.status_code}")

                            if response.status_code == 200:
                                return BytesIO(response.content)
                    except Exception as e:
                        print(f"Resource type {res_type} failed: {e}")
                        continue

            # Fallback to signed URL
            print(f"Trying signed URL approach...")
            signed_url = get_signed_pdf_url(url)
            if signed_url and signed_url != url:
                print(f"Using signed URL: {signed_url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/pdf, image/*'
                }
                response = requests.get(signed_url, headers=headers, timeout=30)
                print(f"Signed URL download status: {response.status_code}")

                if response.status_code == 200:
                    return BytesIO(response.content)

        # Not a Cloudinary URL or all Cloudinary methods failed
        print(f"Trying direct download: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf, image/*'
        }
        response = requests.get(url, headers=headers, timeout=30)

        print(f"Download status for {url}: {response.status_code}")

        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            print(f"Failed to download {url}. Status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        traceback.print_exc()
        return None
