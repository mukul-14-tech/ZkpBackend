#!/usr/bin/env python3
"""
Test script for the decryption API functionality.
This script tests the complete flow: registration -> decryption
"""

import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:8000"

def test_registration_and_decryption():
    """Test the complete registration and decryption flow"""
    
    # Test data
    test_data = {
        "name": "John Doe",
        "age": 30,
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",
        "password": "testpass123"
    }
    
    print("Testing Registration and Decryption Flow")
    print("=" * 50)
    
    # Step 1: Register a user
    print("1. Registering user...")
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"Registration successful!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"Registration request failed: {str(e)}")
        return
    
    # Step 2: Test decryption
    print("\n2. Testing decryption...")
    decrypt_data = {
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/decrypt", json=decrypt_data)
        if response.status_code == 200:
            result = response.json()
            print(f"Decryption successful!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Name: {result['name']}")
            print(f"   Age: {result['age']}")
            print(f"   Similarity Score: {result['similarity_score']:.4f}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"Decryption failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"Decryption request failed: {str(e)}")
    
    # Step 3: Test decryption with wrong password
    print("\n3. Testing decryption with wrong password...")
    wrong_password_data = {
        "fingerprint_image_path": "images/100__M_Left_index_finger.bmp",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/decrypt", json=wrong_password_data)
        if response.status_code == 400:
            print(f"Correctly rejected wrong password!")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"Should have rejected wrong password: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"Wrong password test failed: {str(e)}")

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
    print("Starting Decryption API Tests")
    print("=" * 50)
    
    # Check if API is running
    if not test_api_health():
        print("\nMake sure to start the API server first:")
        print("   python run.py")
        exit(1)
    
    print()
    
    # Run the main test
    test_registration_and_decryption()
    
    print("\nTest completed!")
