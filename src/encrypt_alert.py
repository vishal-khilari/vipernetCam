# src/encrypt_alert.py
import os
from cryptography.fernet import Fernet

KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'keys', 'fernet.key')
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)

def load_or_create_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as f:
            f.write(key)
        return key
    return open(KEY_PATH, 'rb').read()

KEY = load_or_create_key()
CIPHER = Fernet(KEY)

def encrypt_alert_bytes(alert_bytes: bytes) -> bytes:
    """Return encrypted token bytes."""
    return CIPHER.encrypt(alert_bytes)

def decrypt_alert_bytes(token: bytes) -> bytes:
    """Return plaintext bytes (raises if invalid)."""
    return CIPHER.decrypt(token)
