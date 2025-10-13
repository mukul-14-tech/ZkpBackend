# # tests/test_faiss_persistence.py
# import os, sys
# sys.path.append(os.path.abspath("."))

# from app.faiss_store import FaissStore
# import numpy as np

# from app.fp_utils import get_fingerprint_embedding

# def rand_vec(dim):
#     return (np.random.rand(dim).astype("float32") - 0.5).tolist()

# def main():
#     # First run: create and add
#     store1 = FaissStore()
#     dim = store1.dim
#     v = rand_vec(dim)
#     uid = 999
#     store1.add(v, uid)
#     c1 = store1.count()
#     print("Count after write:", c1)

#     # Second run: new instance should load existing index from disk
#     store2 = FaissStore()
#     c2 = store2.count()
#     print("Count after reload:", c2)

#     # Query from new instance
#     D, I = store2.nearest(v, k=1)
#     print("Reloaded nearest id:", I[0])
#     assert I[0] == uid, "Persistence or search mismatch"

# if __name__ == "__main__":
#     main()
