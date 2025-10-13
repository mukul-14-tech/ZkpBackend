# app/key_utils.py
import hashlib
import numpy as np

def generate_key_from_embedding(embedding: list | np.ndarray, password: str) -> bytes:
    """
    Derive a 256-bit AES key from fingerprint embedding + user password.

    Steps:
    1️⃣ Convert the embedding to bytes (float32 → bytes)
    2️⃣ Combine it with password (UTF-8)
    3️⃣ Hash the combined data with SHA-256 → 32-byte AES key
    """
    # ensure embedding is numpy array
    emb_array = np.array(embedding, dtype=np.float32).flatten()
    emb_bytes = emb_array.tobytes()

    # combine embedding bytes + password
    combined = emb_bytes + password.encode("utf-8")

    # SHA-256 hash = deterministic AES key (32 bytes)
    key = hashlib.sha256(combined).digest()

    return key
