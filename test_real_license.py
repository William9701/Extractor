"""
Test script for extracting PII from real driver's license
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_license_extraction():
    """Test extraction with the uploaded Nigerian driver's license"""

    print("=" * 70)
    print("TESTING REAL DRIVER'S LICENSE EXTRACTION")
    print("=" * 70)

    # Path to the license image
    license_path = "WhatsApp Image 2025-11-24 at 13.02.40_28db3157.jpg"

    print(f"\n[1] Reading license image: {license_path}")

    try:
        with open(license_path, "rb") as f:
            files = {"file": (license_path, f, "image/jpeg")}
            data = {
                "profile_id": "william_obi_001",
                "document_type": "driver_license"
            }

            print("[2] Sending extraction request to API...")
            response = requests.post(f"{BASE_URL}/extract", files=files, data=data)

            if response.status_code == 200:
                result = response.json()

                print("\n" + "=" * 70)
                print("EXTRACTION SUCCESSFUL!")
                print("=" * 70)

                print(f"\nProfile ID: {result['profile_id']}")
                print(f"Document Type: {result['document_type']}")
                print(f"Extracted At: {result['extracted_at']}")

                print("\n" + "-" * 70)
                print("EXTRACTED FIELDS:")
                print("-" * 70)

                fields = result['fields']

                print(f"\n{'Field':<20} {'Value':<40} {'Confidence'}")
                print("-" * 70)

                for field_name, field_data in fields.items():
                    value = field_data['value'] or 'N/A'
                    confidence = field_data['confidence']
                    print(f"{field_name:<20} {value:<40} {confidence:.1%}")

                # Expected data from the license:
                print("\n" + "=" * 70)
                print("EXPECTED DATA (from image):")
                print("=" * 70)
                print("Name:         OBI WILLIAM OBIESIE")
                print("DOB:          23-04-1996")
                print("Address:      NO 1 AGBALUSIA NGENE AVENUE, AKWU-OFU, ASABA, DELTA")
                print("License No:   LNO DLT850336AAA43")
                print("Issue Date:   10-08-2021")
                print("Expiry Date:  23-04-2026")

                print("\n" + "=" * 70)
                print("TEST COMPLETED!")
                print("=" * 70)

                return result

            else:
                print(f"\n[ERROR] Extraction failed!")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return None

    except FileNotFoundError:
        print(f"\n[ERROR] License file not found: {license_path}")
        print("Make sure the image is in the current directory")
        return None
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Could not connect to API server at {BASE_URL}")
        print("Make sure the server is running:")
        print("  python app/main.py")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return None


def test_matching():
    """Test matching against extracted data"""
    print("\n\n" + "=" * 70)
    print("TESTING SIMILARITY MATCHING")
    print("=" * 70)

    # Test with exact match
    print("\n[1] Testing with EXACT data:")
    match_data_exact = {
        "profile_id": "william_obi_001",
        "full_name": "Obi William Obiesie",
        "address": "No 1 Agbalusia Ngene Avenue, Akwu-Ofu, Asaba, Delta"
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_exact)

    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")

    # Test with variation
    print("\n[2] Testing with SLIGHT VARIATION:")
    match_data_variant = {
        "profile_id": "william_obi_001",
        "full_name": "William Obi",  # Shortened
        "address": "Agbalusia Avenue, Asaba"  # Abbreviated
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_variant)

    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")

    # Test with wrong data
    print("\n[3] Testing with WRONG data:")
    match_data_wrong = {
        "profile_id": "william_obi_001",
        "full_name": "John Smith",
        "address": "123 Main Street, Lagos"
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_wrong)

    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")


def test_search():
    """Test semantic search"""
    print("\n\n" + "=" * 70)
    print("TESTING SEMANTIC SEARCH")
    print("=" * 70)

    queries = ["William", "Obi", "Asaba", "Delta"]

    for query in queries:
        print(f"\n[Query: '{query}']")
        response = requests.get(f"{BASE_URL}/search", params={"query": query, "limit": 3})

        if response.status_code == 200:
            result = response.json()
            if result['results']:
                for i, res in enumerate(result['results'], 1):
                    print(f"  {i}. {res['full_name']} (similarity: {res['similarity_score']:.1%})")
            else:
                print("  No results found")


if __name__ == "__main__":
    # Run extraction test
    extraction_result = test_real_license_extraction()

    if extraction_result:
        # Run matching tests
        test_matching()

        # Run search tests
        test_search()

        print("\n\n" + "=" * 70)
        print("ALL TESTS COMPLETED!")
        print("=" * 70)
        print("\nNote: If OpenAI API key is not configured, extraction uses mock data.")
        print("All other features (matching, search) work with real algorithms.")
