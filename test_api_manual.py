"""
Manual API testing script
Run this to test the API endpoints manually
"""
import requests
import json
from pathlib import Path
from PIL import Image
from io import BytesIO


BASE_URL = "http://localhost:8000"


def create_test_image():
    """Create a simple test image"""
    img = Image.new("RGB", (800, 600), color="white")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health():
    """Test health check"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_extraction():
    """Test document extraction"""
    print("\n=== Testing Extraction Endpoint ===")

    # Create test image
    img_bytes = create_test_image()

    files = {"file": ("test_document.png", img_bytes, "image/png")}
    data = {"profile_id": "test_user_123", "document_type": "driver_license"}

    response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Profile ID: {result['profile_id']}")
        print(f"Document Type: {result['document_type']}")
        print("\nExtracted Fields:")
        for field_name, field_data in result["fields"].items():
            print(f"  {field_name}: {field_data['value']} (confidence: {field_data['confidence']})")
    else:
        print(f"Error: {response.text}")


def test_matching():
    """Test similarity matching"""
    print("\n=== Testing Matcher Endpoint ===")

    data = {
        "profile_id": "test_user_123",
        "full_name": "John Doe",
        "address": "123 Main Street, San Jose CA 95110",
    }

    response = requests.post(f"{BASE_URL}/match", json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Name Similarity: {result['name_similarity']:.3f}")
        print(f"Address Similarity: {result['address_similarity']:.3f}")
        print(f"Overall Score: {result['overall_score']:.3f}")
        print(f"Classification: {result['classification']}")
    else:
        print(f"Error: {response.text}")


def test_pdf_generation():
    """Test PDF generation"""
    print("\n=== Testing PDF Generation Endpoint ===")

    data = {
        "form_type": "sample_form",
        "fields": {
            "full_name": "Jane Smith",
            "dob": "1985-05-20",
            "address": "456 Oak Avenue, San Francisco CA 94102",
            "id_number": "DL87654321",
            "expiry_date": "2030-05-20",
        },
    }

    response = requests.post(f"{BASE_URL}/prefill-pdf", json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        # Save PDF
        output_path = "test_filled_form.pdf"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"PDF saved to: {output_path}")
        print(f"PDF size: {len(response.content)} bytes")
    else:
        print(f"Error: {response.text}")


def test_consent_flow():
    """Test consent token creation and redemption"""
    print("\n=== Testing Consent Flow ===")

    # Create token
    print("\n1. Creating consent token...")
    create_data = {
        "profile_id": "test_user_123",
        "fields_allowed": ["full_name", "dob"],
    }

    response = requests.post(f"{BASE_URL}/consent/create", json=create_data)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    result = response.json()
    token = result["token"]
    expires_at = result["expires_at"]

    print(f"Token created successfully")
    print(f"Token (first 50 chars): {token[:50]}...")
    print(f"Expires at: {expires_at}")

    # Redeem token
    print("\n2. Redeeming consent token...")
    response = requests.get(f"{BASE_URL}/consent/redeem", params={"token": token})
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("Allowed fields:")
        for field_name, field_value in result.items():
            print(f"  {field_name}: {field_value}")
    else:
        print(f"Error: {response.text}")

    # Test with invalid token
    print("\n3. Testing with invalid token...")
    response = requests.get(
        f"{BASE_URL}/consent/redeem", params={"token": "invalid_token"}
    )
    print(f"Status: {response.status_code}")
    print(f"Expected 401, got: {response.status_code}")


def test_search():
    """Test semantic search"""
    print("\n=== Testing Search Endpoint ===")

    response = requests.get(f"{BASE_URL}/search", params={"query": "John", "limit": 5})
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Query: {result['query']}")
        print(f"Results: {len(result['results'])} found")

        for i, res in enumerate(result["results"], 1):
            print(f"\n  Result {i}:")
            print(f"    Profile ID: {res['profile_id']}")
            print(f"    Name: {res['full_name']}")
            print(f"    Address: {res['address']}")
            print(f"    Similarity: {res['similarity_score']:.3f}")
    else:
        print(f"Error: {response.text}")


def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("Starting API Manual Tests")
    print("=" * 60)

    try:
        test_root()
        test_health()
        test_extraction()
        test_matching()
        test_pdf_generation()
        test_consent_flow()
        test_search()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Start it with: python app/main.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
