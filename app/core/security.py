import base64
import json
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from app.config import settings


def _get_key() -> bytes:
    """
    Derive a 256-bit key from SECRET_KEY
    """
    return sha256(settings.SECRET_KEY.encode()).digest()


def encrypt_value(value: str) -> str:
    """
    Encrypt a string using AES-256 GCM
    Returns base64 encoded JSON payload
    """
    key = _get_key()

    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(value.encode())

    payload = {
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(tag).decode()
    }

    return base64.b64encode(json.dumps(payload).encode()).decode()


def decrypt_value(value: str) -> str:
    """
    Decrypt AES-256 GCM payload
    """
    key = _get_key()

    decoded = base64.b64decode(value).decode()
    payload = json.loads(decoded)

    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["ciphertext"])
    tag = base64.b64decode(payload["tag"])

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    decrypted = cipher.decrypt_and_verify(ciphertext, tag)

    return decrypted.decode()