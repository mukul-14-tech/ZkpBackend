# Decryption API Documentation

## Overview

The decryption API allows users to verify their identity using their fingerprint and password, then decrypt their stored personal data. This follows the same security model as the encryption process but in reverse.

## API Endpoints

### POST /decrypt

Decrypts user data using fingerprint verification and password.

#### Request Body

```json
{
    "fingerprint_image_path": "path/to/fingerprint/image.bmp",
    "password": "user_password"
}
```

#### Response

**Success (200):**
```json
{
    "user_id": 1,
    "name": "John Doe",
    "age": 30,
    "status": "success",
    "message": "User data decrypted successfully",
    "similarity_score": 0.9876
}
```

**Error (400/404):**
```json
{
    "detail": "Error message describing what went wrong"
}
```

## How It Works

1. **Fingerprint Processing**: The provided fingerprint image is processed to generate an embedding vector
2. **Similarity Search**: The embedding is compared against all stored embeddings in the FaissStore to find the best match
3. **User Identification**: The highest matching user ID is retrieved from the similarity search
4. **Data Retrieval**: The encrypted user data (name, age) is retrieved from PostgreSQL using the matched user ID
5. **Key Generation**: The same AES key is generated using the fingerprint embedding + password combination
6. **Decryption**: The encrypted data is decrypted using the generated key
7. **Response**: The decrypted data along with similarity score is returned

## Security Features

- **Fingerprint Verification**: Only users with matching fingerprints can access their data
- **Password Protection**: Even with a matching fingerprint, the correct password is required
- **Similarity Scoring**: The API returns a similarity score to indicate how well the fingerprint matched
- **No Data Storage**: Fingerprint embeddings are not stored during decryption - only used for comparison

## Error Handling

- **404 Not Found**: No matching fingerprint found in the system
- **400 Bad Request**: Various errors including:
  - Invalid fingerprint image
  - Decryption failure (wrong password)
  - Invalid request format

## Usage Example

```python
import requests

# Decrypt user data
decrypt_data = {
    "fingerprint_image_path": "images/user_fingerprint.bmp",
    "password": "user_password"
}

response = requests.post("http://localhost:8000/decrypt", json=decrypt_data)

if response.status_code == 200:
    result = response.json()
    print(f"Welcome {result['name']}, age {result['age']}")
    print(f"Fingerprint match: {result['similarity_score']:.2%}")
else:
    print(f"Error: {response.json()['detail']}")
```

## Testing

Run the test script to verify the decryption functionality:

```bash
python test_decryption.py
```

Make sure the API server is running first:

```bash
python run.py
```



