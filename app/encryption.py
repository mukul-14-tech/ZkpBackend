from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def encrypt_data(data: str, key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt data using AES-GCM.
    Returns: (encrypted_data, nonce, tag)
    """
    # Generate random nonce
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    
    # Create cipher
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Encrypt data
    encrypted_data = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    
    return encrypted_data, nonce, encryptor.tag

def decrypt_data(encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes) -> str:
    """
    Decrypt data using AES-GCM.
    """
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.decode('utf-8')