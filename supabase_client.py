import os
from typing import Optional

# Import the initialized Supabase client from the database module
try:
    from database import supabase
except ImportError:
    supabase = None

# Bucket name from environment variables (as defined in .env)
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "happy-vision")

def _ensure_client() -> bool:
    """Check that Supabase client and bucket are configured."""
    return supabase is not None and SUPABASE_BUCKET is not None

def upload_image(local_path: str, remote_path: str) -> bool:
    """Upload a local file to Supabase Storage.

    Parameters
    ----------
    local_path: str
        Absolute path to the file on the local filesystem.
    remote_path: str
        Desired path inside the bucket (e.g., "logos/logo.png").

    Returns
    -------
    bool
        True if the upload succeeded, False otherwise.
    """
    if not _ensure_client():
        return False
    try:
        # Read file bytes
        with open(local_path, "rb") as f:
            data = f.read()
        # Upload – upsert so repeated uploads replace the previous file
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(remote_path, data, {"upsert": True})
        # The Supabase SDK returns a dict with a "error" key when something fails
        if res.get("error"):
            print(f"[Supabase] Upload error: {res['error']}")
            return False
        return True
    except Exception as e:
        print(f"[Supabase] Exception during upload_image: {e}")
        return False

def public_url(path: str, expires_in: int = 3600) -> Optional[str]:
    """Generate a signed URL for a private object.

    Parameters
    ----------
    path: str
        Path inside the bucket (e.g., "logos/logo.png").
    expires_in: int, optional
        Seconds until the URL expires. Default is 1 hour.

    Returns
    -------
    Optional[str]
        The signed URL if successful, otherwise ``None``.
    """
    if not _ensure_client():
        return None
    try:
        res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(path, expires_in)
        # Expected format: {"signedURL": "https://...", "error": None}
        if res.get("error"):
            print(f"[Supabase] Signed URL error: {res['error']}")
            return None
        return res.get("signedURL")
    except Exception as e:
        print(f"[Supabase] Exception during public_url: {e}")
        return None

def delete_image(path: str) -> bool:
    """Delete an object from the bucket.

    Returns ``True`` on success, ``False`` otherwise.
    """
    if not _ensure_client():
        return False
    try:
        res = supabase.storage.from_(SUPABASE_BUCKET).remove([path])
        if res.get("error"):
            print(f"[Supabase] Delete error: {res['error']}")
            return False
        return True
    except Exception as e:
        print(f"[Supabase] Exception during delete_image: {e}")
        return False
