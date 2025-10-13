# app/fp_utils.py
import cv2
import numpy as np
import hashlib

# -----------------------------
# 1️⃣ Function: image → embedding vector
# -----------------------------
def get_fingerprint_embedding(image_path: str) -> np.ndarray:
    """
    Reads a fingerprint image (.bmp, .png, etc.) and returns a normalized embedding vector.
    This version uses pure OpenCV and NumPy — no torchvision.
    """


    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    # Resize to fixed size for consistency
    img = cv2.resize(img, (224, 224))

    # Normalize pixel intensities
    img = img.astype(np.float32) / 255.0

    # Optional image enhancement (sharpening / contrast)
    img = cv2.equalizeHist((img * 255).astype(np.uint8)).astype(np.float32) / 255.0

    # Simple handcrafted embedding — compute various statistics + features
    # 1. Flatten part of image
    patch = cv2.resize(img, (32, 32)).flatten()

    # 2. Compute gradients (texture features)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    grad_features = cv2.resize(mag, (32, 32)).flatten()

    # 3. Combine + normalize
    combined = np.concatenate([patch, grad_features])
    embedding = combined / np.linalg.norm(combined)

    if embedding.shape[0] != 128:
        embedding = np.resize(embedding, 128)

    return embedding.astype(np.float32)


# -----------------------------
# 2️⃣ Function: compare two fingerprints
# -----------------------------
def compare_fingerprints(img_path: str, stored_embedding: np.ndarray) -> float:
    """
    Takes a fingerprint image and a reference embedding, and returns cosine similarity [0,1].
    """
    new_emb = get_fingerprint_embedding(img_path)
    sim = np.dot(new_emb, stored_embedding) / (np.linalg.norm(new_emb) * np.linalg.norm(stored_embedding))
    return float(sim)


# -----------------------------
# 3️⃣ Function: embedding + code → SHA-256 hash
# -----------------------------
def embedding_to_sha256(embedding: np.ndarray, code: str) -> str:
    """
    Converts a fingerprint embedding and an alphanumeric code
    into a deterministic SHA-256 hex string.
    """
    if not isinstance(code, str) or len(code) != 6 or not code.isalnum():
        raise ValueError("Code must be a 6-character alphanumeric string (e.g., 'A1B2C3').")

    arr_bytes = embedding.tobytes()
    combined = arr_bytes + code.encode('utf-8')
    sha256_hash = hashlib.sha256(combined).hexdigest()
    return sha256_hash


# -----------------------------
# 4️⃣ Function: image → SHA-256 hash
# -----------------------------
def image_to_fingerprint_hash(image_path: str, code: str) -> str:
    """
    Complete pipeline:
    1️⃣ Image → embedding
    2️⃣ Embedding + code → SHA-256 hash
    Returns hash string.
    """
    embedding = get_fingerprint_embedding(image_path)
    sha_hash = embedding_to_sha256(embedding, code)
    return sha_hash


# -----------------------------
# 5️⃣ Manual test
# -----------------------------
if __name__ == "__main__":
    img_path = "demo_finger/100__M_Left_index_finger.bmp"
    code = "BX19D0"
    emb = get_fingerprint_embedding(img_path)
    print(f"Embedding length: {len(emb)} | First 5 values: {emb[:5]}")
    hash_val = image_to_fingerprint_hash(img_path, code)
    print(f"Fingerprint SHA-256 hash for {img_path} → {hash_val}")
