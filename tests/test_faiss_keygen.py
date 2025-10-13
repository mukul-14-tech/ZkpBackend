import os, sys, json, binascii
import numpy as np

sys.path.append(os.path.abspath("."))

from app.faiss_store import FaissStore
from app.key_utils import generate_key_from_embedding
from app.fp_utils import get_fingerprint_embedding

# Path to store all embeddings
DATA_PATH = "data/embeddings.json"


def load_existing_data():
    """Load existing embeddings from JSON file (if any)"""
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    """Save updated embeddings back to JSON file"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\n💾 Data saved to {DATA_PATH}")


def main():
    store = FaissStore()
    store.reset_index()  # start fresh each time

    dim = store.dim
    print(f"\nEmbedding dimension: {dim}")

    # Load old data
    data = load_existing_data()
    print(f"📂 Loaded {len(data)} existing users from JSON file.")

    # Add new sample users
    new_users = [
       {"user_id": 101, "img": "images/100__M_Left_index_finger.bmp", "password": "ABC@397"},
        
    ]

    for user in new_users:
        # ✅ embedding is now a numpy array (no .numpy() or .squeeze())
        embedding = get_fingerprint_embedding(user["img"])

        # generate AES key using embedding + password
        key = generate_key_from_embedding(embedding, user["password"])

        # add to store
        store.add(embedding, user["user_id"])

        # Add entry to JSON memory
        entry = {
            "user_id": user['user_id'],
            "embedding": embedding.tolist(),
            "aes_key_hex": binascii.hexlify(key).decode()
        }
        data.append(entry)

        print(f"\nUser ID: {user['user_id']}")
        print(f"Embedding (first 5 dims): {embedding[:5]} ...")
        print(f"Derived AES Key (hex): {entry['aes_key_hex']}")

    # Save all data
    save_data(data)

    print("\n✅ Added all embeddings successfully.")
    print("Total embeddings now:", len(data))

    # Show stored data
    print("\n📋 Stored Embeddings (from JSON):")
    for entry in data:
        print(f"User ID: {entry['user_id']}")
        print(f"  Key (hex): {entry['aes_key_hex'][:32]}...")
        print(f"  Embedding (first 5 dims): {entry['embedding'][:5]} ...\n")


if __name__ == "__main__":
    main()
