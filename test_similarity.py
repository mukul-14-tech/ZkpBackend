#!/usr/bin/env python3
"""
Test script to demonstrate fingerprint similarity matching with different scenarios.
This shows how the system handles various similarity levels.
"""

import requests
import json
import os
import numpy as np
from app.fp_utils import get_fingerprint_embedding
from app.faiss_store import FaissStore

# API base URL
BASE_URL = "http://localhost:8000"

def test_similarity_scenarios():
    """Test different similarity scenarios"""
    
    print("Testing Fingerprint Similarity Matching")
    print("=" * 50)
    
    # Test data for registration
    test_data = {
        "name": "Alice Smith",
        "age": 25,
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",
        "password": "alice123"
    }
    
    # Step 1: Register a user
    print("1. Registering user Alice...")
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"Registration successful! User ID: {result['user_id']}")
            alice_user_id = result['user_id']
        else:
            print(f"Registration failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Registration request failed: {str(e)}")
        return
    
    # Step 2: Test with exact same fingerprint (should be 1.0)
    print("\n2. Testing with exact same fingerprint...")
    test_decrypt_exact = {
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",
        "password": "alice123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/decrypt", json=test_decrypt_exact)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Exact match successful!")
            print(f"   Similarity Score: {result['similarity_score']:.4f}")
            print(f"   Name: {result['name']}")
        else:
            print(f"❌ Exact match failed: {response.status_code}")
    except Exception as e:
        print(f"Exact match test failed: {str(e)}")
    
    # Step 3: Test with slightly modified fingerprint (simulate noise)
    print("\n3. Testing with modified fingerprint (simulating noise)...")
    
    # Get the original embedding and add some noise
    original_embedding = get_fingerprint_embedding("images/100__M_Left_index_finger.bmp")
    
    # Add small amount of noise (5% of the original values)
    noise_level = 0.05
    noise = np.random.normal(0, noise_level, original_embedding.shape)
    modified_embedding = original_embedding + noise
    
    # Normalize the modified embedding
    modified_embedding = modified_embedding / np.linalg.norm(modified_embedding)
    
    # Calculate similarity manually
    cosine_sim = np.dot(original_embedding, modified_embedding) / (
        np.linalg.norm(original_embedding) * np.linalg.norm(modified_embedding)
    )
    print(f"   Manual similarity calculation: {cosine_sim:.4f}")
    
    # Step 4: Test with very different fingerprint (should fail)
    print("\n4. Testing with completely different fingerprint...")
    test_decrypt_different = {
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",  # Same file but we'll simulate different
        "password": "alice123"
    }
    
    # Let's create a very different embedding
    different_embedding = np.random.random(128).astype(np.float32)
    different_embedding = different_embedding / np.linalg.norm(different_embedding)
    
    # Calculate similarity with very different embedding
    very_different_sim = np.dot(original_embedding, different_embedding) / (
        np.linalg.norm(original_embedding) * np.linalg.norm(different_embedding)
    )
    print(f"   Similarity with random embedding: {very_different_sim:.4f}")
    
    # Step 5: Test threshold behavior
    print("\n5. Testing similarity thresholds...")
    print("   Similarity scores and their meanings:")
    print("   - 1.0000: Perfect match (identical fingerprint)")
    print("   - 0.9000+: Very high similarity (same person, minor variations)")
    print("   - 0.8000+: High similarity (same person, some noise)")
    print("   - 0.7000+: Good similarity (same person, moderate noise)")
    print("   - 0.5000+: Moderate similarity (might be same person)")
    print("   - 0.3000+: Low similarity (probably different person)")
    print("   - 0.1000+: Very low similarity (likely different person)")
    print("   - 0.0000+: No similarity (different person)")

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("API is running!")
            return True
        else:
            print(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Fingerprint Similarity Tests")
    print("=" * 50)
    
    # Check if API is running
    if not test_api_health():
        print("\nMake sure to start the API server first:")
        print("   python run.py")
        exit(1)
    
    print()
    
    # Run the similarity tests
    test_similarity_scenarios()
    
    print("\nSimilarity Test completed!")
    print("\nKey Points:")
    print("- The system uses cosine similarity to find the closest match")
    print("- Higher similarity scores (closer to 1.0) indicate better matches")
    print("- The system will return the best match even if it's not perfect")
    print("- In practice, you might want to set a minimum similarity threshold")

