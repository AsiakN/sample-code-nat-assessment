import os
from cryptography.fernet import Fernet
from loguru import logger

# Load the Fernet key from an environment variable
FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())


def encrypt_field(value: str) -> str:
    """Encrypt a field before saving to the database."""
    return fernet.encrypt(value.encode()).decode()


def decrypt_field(value: str) -> str:
    """Decrypt a field after retrieving from the database."""
    return fernet.decrypt(value).decode()
