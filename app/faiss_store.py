import os
import json
import numpy as np
from threading import Lock
from dotenv import load_dotenv
import hashlib  # for secure hash-based key derivation

# Load .env (if any)
load_dotenv()

JSON_PATH = os.getenv("FAISS_JSON_PATH", "./data/embeddings.json")
EMBED_DIM = int(os.getenv("EMBED_DIM", "128"))


class FaissStore:
    """
    Simplified JSON-based embedding store.
    - Keeps user_id → embedding mapping
    - Generates AES key from (embedding + password)
    - Persists everything in embeddings.json
    """

    def __init__(self, dim: int = EMBED_DIM):
        self.dim = dim
        self.lock = Lock()
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        self.data = self._load_json()
        print(f"Loaded {len(self.data)} embeddings from {JSON_PATH}")

    # ------------------------------------------------
    # Core operations
    # ------------------------------------------------
    def reset_index(self):
        """Clear all stored embeddings from JSON."""
        with self.lock:
            self.data = {}
            if os.path.exists(JSON_PATH):
                os.remove(JSON_PATH)
            print("Cleared all stored embeddings.")

    def add(self, embedding, user_id: int):
        """Add new embedding to JSON store."""
        try:
            vec = np.asarray(embedding, dtype=np.float32).flatten().tolist()
            if len(vec) != self.dim:
                raise ValueError(f"Embedding dimension mismatch: expected {self.dim}, got {len(vec)}")

            with self.lock:
                self.data[str(user_id)] = vec
                print(f"DEBUG: Added user_id={user_id} to data dict")
                self._save_json()
                print(f"DEBUG: Saved to JSON file")
            print(f"Added embedding for user_id={user_id}")
        except Exception as e:
            print(f"ERROR in FaissStore.add: {str(e)}")
            raise

    def add_and_generate_key(self, embedding, password: str, user_id: int):
        """
        Add embedding to JSON and generate AES-256 key
        using (embedding + password).
        """
        self.add(embedding, user_id)

        # Derive key = SHA256(embedding_bytes + password_bytes)
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        password_bytes = password.encode("utf-8")
        combined = embedding_bytes + password_bytes
        key = hashlib.sha256(combined).digest()  # 32-byte AES key

        return key

    def count(self) -> int:
        """Return total stored embeddings."""
        return len(self.data)

    def get_all_embeddings(self):
        """Return list of (user_id, embedding)."""
        return [(int(uid), emb) for uid, emb in self.data.items()]

    def search_similar(self, query_embedding, k: int = 1):
        """
        Search for the most similar embedding(s) to the query.
        Returns list of (user_id, similarity_score) tuples, sorted by similarity (highest first).
        """
        if not self.data:
            return []
        
        query_vec = np.asarray(query_embedding, dtype=np.float32).flatten()
        if len(query_vec) != self.dim:
            raise ValueError(f"Query embedding dimension mismatch: expected {self.dim}, got {len(query_vec)}")
        
        similarities = []
        for user_id_str, stored_embedding in self.data.items():
            stored_vec = np.array(stored_embedding, dtype=np.float32)
            
            # Calculate cosine similarity
            dot_product = np.dot(query_vec, stored_vec)
            norm_query = np.linalg.norm(query_vec)
            norm_stored = np.linalg.norm(stored_vec)
            
            if norm_query == 0 or norm_stored == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_query * norm_stored)
            
            similarities.append((int(user_id_str), float(similarity)))
        
        # Sort by similarity (highest first) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    # ------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------
    def _load_json(self):
        """Load existing embeddings safely, even if file is empty/corrupt."""
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r") as f:
                    content = f.read().strip()
                    if not content:
                        print("Empty JSON file detected — resetting store.")
                        return {}
                    return json.loads(content)
            except json.JSONDecodeError:
                print("Invalid JSON detected — resetting store.")
                return {}
        return {}

    def _save_json(self):
        try:
            print(f"DEBUG: Saving to {JSON_PATH}")
            print(f"DEBUG: Data contains {len(self.data)} entries")
            with open(JSON_PATH, "w") as f:
                json.dump(self.data, f, indent=4)
            print(f"DEBUG: Successfully saved to {JSON_PATH}")
        except Exception as e:
            print(f"ERROR in _save_json: {str(e)}")
            raise
