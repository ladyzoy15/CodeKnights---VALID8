import hashlib
import secrets
from datetime import datetime, timedelta, timezone

def generate_reset_token() -> str:
    """Generates a secure random token for password resets."""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hashes a token using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()

def get_token_expiry(hours: int = 2) -> datetime:
    """Calculates token expiry time."""
    return datetime.now(timezone.utc) + timedelta(hours=hours)
