# tests/test_faiss_add_and_search.py
import os, sys
sys.path.append(os.path.abspath("."))

from app.faiss_store import FaissStore
import numpy as np
import os

from app.fp_utils import get_fingerprint_embedding

def rand_vec(dim):
    return (np.random.rand(dim).astype("float32") - 0.5).tolist()

def embedding_from_image(image_path):
    return get_fingerprint_embedding(image_path).numpy().squeeze().tolist()

def main():
    # Clean previous index for a fresh run (optional)
    idx_path = os.getenv("FAISS_INDEX_PATH", "./faiss_index.index")
    if os.path.exists(idx_path):
        os.remove(idx_path)

    store = FaissStore()
    dim = store.dim
    print("EMBED_DIM:", dim)

    v1 = rand_vec(dim)
    v2 = rand_vec(dim)
    v3 = rand_vec(dim)

    store.add(v1, 101)
    store.add(v2, 202)
    store.add(v3, 303)
    print("Count after adds:", store.count())

    D, I = store.nearest(v1, k=3)
    print("Query distances:", D)
    print("Query ids      :", I)

    # sanity: first result should be the same id we added with v1
    assert I[0] == 101, "Nearest neighbor mismatch"

if __name__ == "__main__":
    main()
