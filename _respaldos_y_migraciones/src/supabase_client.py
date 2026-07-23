import os
from supabase import create_client, Client

# Initialize Supabase client using environment variables
supabase: Client = None
if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

BUCKET = os.getenv('SUPABASE_BUCKET')

def public_url(path: str) -> str:
    """Return a signed public URL for a private bucket object.
    The URL is valid for 1 hour (3600 seconds)."""
    if not supabase or not BUCKET:
        return ''
    # Supabase storage signed URLs require expiration in seconds.
    # Use 3600 seconds (1 hour) by default.
    try:
        res = supabase.storage.from_(BUCKET).create_signed_url(path, 3600)
        # The response format is {'signedURL': ['...']}
        if isinstance(res, dict):
            url = res.get('signedURL', [])
            if isinstance(url, list) and url:
                return url[0]
        # Fallback for older SDK versions returning list directly
        if isinstance(res, list) and res:
            return res[0]
    except Exception as e:
        print(f"[supabase_client] Error generating signed URL for {path}: {e}")
    return ''

def upload_image(local_path: str, remote_path: str) -> str:
    """Upload a local file to the bucket and return its public URL.
    remote_path should include folder prefix, e.g. "logos/logo.png".
    """
    if not supabase or not BUCKET:
        return ''
    try:
        with open(local_path, 'rb') as f:
            supabase.storage.from_(BUCKET).upload(remote_path, f.read())
        return public_url(remote_path)
    except Exception as e:
        print(f"[supabase_client] Upload failed for {local_path} -> {remote_path}: {e}")
        return ''
