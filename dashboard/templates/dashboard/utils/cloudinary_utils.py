# dashboard/utils/cloudinary_utils.py
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
        # Pattern to match Cloudinary URLs - use raw string
        pattern = r'upload/(v\d+)/(.*?\.(pdf|jpg|jpeg|png))'
        match = re.search(pattern, url, re.IGNORECASE)

        if match:
            public_id_with_ext = match.group(2)
            # Remove file extension
            public_id = public_id_with_ext.rsplit('.', 1)[0]
            return public_id

        return None
    except Exception as e:
        print(f"Error extracting public_id: {e}")
        return None


def get_signed_pdf_url(original_url):
    """
    Convert regular Cloudinary URL to signed URL
    """
    try:
        public_id = extract_public_id_from_url(original_url)

        if public_id:
            # Generate signed URL
            signed_url, options = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type='raw',
                secure=True,
                sign_url=True  # This adds authentication
            )
            print(f"Generated signed URL for: {public_id}")
            return signed_url

        print(f"Could not extract public_id from: {original_url}")
        return original_url  # Return original if we can't parse

    except Exception as e:
        print(f"Error generating signed URL: {e}")
        traceback.print_exc()
        return original_url


def download_certificate_with_auth(url):
    """
    Download certificate from Cloudinary with proper authentication
    """
    try:
        print(f"Attempting to download with authentication: {url}")

        # Get signed URL if it's a Cloudinary URL
        if 'cloudinary.com' in url:
            signed_url = get_signed_pdf_url(url)
            download_url = signed_url
            print(f"Using signed URL: {signed_url}")
        else:
            download_url = url

        # Download with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf, image/*'
        }

        response = requests.get(download_url, headers=headers, timeout=30)

        print(f"Download status for {url}: {response.status_code}")

        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            print(f"Failed to download {download_url}. Status: {response.status_code}")
            print(f"Response headers: {response.headers}")

            # Try one more time with the original URL if signed URL failed
            if download_url != url:
                print(f"Trying with original URL: {url}")
                response2 = requests.get(url, headers=headers, timeout=30)
                if response2.status_code == 200:
                    return BytesIO(response2.content)

            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        traceback.print_exc()
        return None