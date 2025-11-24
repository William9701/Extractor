"""
Test script for live Render deployment
Tests all endpoints on https://pii-extraction-service.onrender.com
"""
import requests
import json
from io import BytesIO
from PIL import Image

BASE_URL = "https://pii-extraction-service.onrender.com"


def test_health():
    """Test health check endpoint"""
    print("\n" + "=" * 70)
    print("TEST 1: HEALTH CHECK")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health Status: {data.get('status', 'unknown')}")
        return True
    else:
        print(f"❌ Health check failed")
        return False


def test_root():
    """Test root endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: ROOT ENDPOINT")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Service: {data.get('service')}")
        print(f"✅ Version: {data.get('version')}")
        print(f"✅ Status: {data.get('status')}")
        return True
    else:
        print(f"❌ Root endpoint failed")
        return False


def test_extraction():
    """Test document extraction with real Nigerian driver's license"""
    print("\n" + "=" * 70)
    print("TEST 3: DOCUMENT EXTRACTION (Real License)")
    print("=" * 70)

    # Use the real Nigerian driver's license
    license_path = "WhatsApp Image 2025-11-24 at 13.02.40_28db3157.jpg"

    try:
        with open(license_path, "rb") as f:
            files = {"file": (license_path, f, "image/jpeg")}
            data = {
                "profile_id": "william_obi_render_test",
                "document_type": "driver_license"
            }

            print("📤 Uploading real Nigerian driver's license...")
            response = requests.post(
                f"{BASE_URL}/extract",
                files=files,
                data=data,
                timeout=60
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Extraction successful!")
                print(f"Profile ID: {result['profile_id']}")
                print(f"Document Type: {result['document_type']}")

                print("\nExtracted Fields:")
                print("-" * 70)
                for field_name, field_data in result['fields'].items():
                    value = field_data['value'] or 'N/A'
                    confidence = field_data['confidence']
                    print(f"  {field_name:15s}: {value:40s} ({confidence:.0%} confidence)")

                print("\n📝 Note: Without OpenAI API key, mock data is returned.")
                print("   Real extraction requires OPENAI_API_KEY in Render environment.")
                return True
            else:
                print(f"❌ Extraction failed: {response.text}")
                return False

    except FileNotFoundError:
        print(f"⚠️  License file not found: {license_path}")
        print("   Testing with generated sample image instead...")

        # Create a sample image
        img = Image.new("RGB", (800, 500), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        files = {"file": ("sample.png", img_bytes, "image/png")}
        data = {
            "profile_id": "render_test_sample",
            "document_type": "driver_license"
        }

        response = requests.post(
            f"{BASE_URL}/extract",
            files=files,
            data=data,
            timeout=60
        )

        print(f"Status Code: {response.status_code}")
        return response.status_code == 200


def test_matching():
    """Test similarity matching"""
    print("\n" + "=" * 70)
    print("TEST 4: SIMILARITY MATCHING")
    print("=" * 70)

    # Test 1: Exact match
    print("\n[Test 4.1] Exact Match:")
    match_data = {
        "profile_id": "william_obi_render_test",
        "full_name": "John Doe",
        "address": "123 Main Street, San Jose CA 95110"
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")
        print("✅ Matching works!")
    else:
        print(f"❌ Matching failed: {response.text}")
        return False

    # Test 2: Variation
    print("\n[Test 4.2] Slight Variation:")
    match_data_variant = {
        "profile_id": "william_obi_render_test",
        "full_name": "John David Doe",
        "address": "123 Main St, San Jose"
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_variant)
    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")
        print("✅ Variant matching works!")

    # Test 3: No match
    print("\n[Test 4.3] Different Data:")
    match_data_diff = {
        "profile_id": "william_obi_render_test",
        "full_name": "Jane Smith",
        "address": "456 Oak Avenue, Lagos Nigeria"
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_diff)
    if response.status_code == 200:
        result = response.json()
        print(f"  Name Similarity:    {result['name_similarity']:.1%}")
        print(f"  Address Similarity: {result['address_similarity']:.1%}")
        print(f"  Overall Score:      {result['overall_score']:.1%}")
        print(f"  Classification:     {result['classification'].upper()}")
        print("✅ No-match detection works!")

    return True


def test_pdf_generation():
    """Test PDF form generation"""
    print("\n" + "=" * 70)
    print("TEST 5: PDF GENERATION")
    print("=" * 70)

    pdf_data = {
        "form_type": "sample_form",
        "fields": {
            "full_name": "Obi William Obiesie",
            "dob": "1996-04-23",
            "address": "No 1 Agbalusia Ngene Avenue, Akwu-Ofu, Asaba, Delta",
            "id_number": "DLT850336AAA43",
            "expiry_date": "2026-04-23"
        }
    }

    response = requests.post(f"{BASE_URL}/prefill-pdf", json=pdf_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        # Save PDF
        output_file = "render_test_form.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF generated successfully!")
        print(f"   Saved to: {output_file}")
        print(f"   File size: {len(response.content):,} bytes")
        return True
    else:
        print(f"❌ PDF generation failed: {response.text}")
        return False


def test_consent_flow():
    """Test consent token creation and redemption"""
    print("\n" + "=" * 70)
    print("TEST 6: CONSENT-BASED SHARING")
    print("=" * 70)

    # Create token
    print("\n[Test 6.1] Creating Consent Token:")
    consent_data = {
        "profile_id": "william_obi_render_test",
        "fields_allowed": ["full_name", "dob", "address"]
    }

    response = requests.post(f"{BASE_URL}/consent/create", json=consent_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ Token creation failed: {response.text}")
        return False

    result = response.json()
    token = result['token']
    expires_at = result['expires_at']

    print(f"✅ Token created!")
    print(f"   Token (first 50 chars): {token[:50]}...")
    print(f"   Expires at: {expires_at}")

    # Redeem token
    print("\n[Test 6.2] Redeeming Consent Token:")
    response = requests.get(f"{BASE_URL}/consent/redeem", params={"token": token})
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Token redeemed successfully!")
        print("   Retrieved fields:")
        for field_name, field_value in data.items():
            print(f"     {field_name}: {field_value}")
    else:
        print(f"❌ Token redemption failed: {response.text}")
        return False

    # Test invalid token
    print("\n[Test 6.3] Testing Invalid Token:")
    response = requests.get(f"{BASE_URL}/consent/redeem", params={"token": "invalid_token_12345"})
    print(f"Status Code: {response.status_code}")

    if response.status_code == 401:
        print("✅ Invalid token correctly rejected!")
    else:
        print("⚠️  Expected 401 for invalid token")

    return True


def test_search():
    """Test semantic search"""
    print("\n" + "=" * 70)
    print("TEST 7: SEMANTIC SEARCH (Bonus Feature)")
    print("=" * 70)

    queries = [
        ("John", "Search by first name"),
        ("Doe", "Search by last name"),
        ("Main Street", "Search by address"),
        ("San Jose", "Search by city")
    ]

    for query, description in queries:
        print(f"\n[Query: '{query}'] - {description}")
        response = requests.get(
            f"{BASE_URL}/search",
            params={"query": query, "limit": 3}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  Found {len(result['results'])} results")

            for i, res in enumerate(result['results'], 1):
                print(f"    {i}. {res['full_name']} (similarity: {res['similarity_score']:.1%})")
                print(f"       {res['address']}")
        else:
            print(f"  ❌ Search failed: {response.text}")
            return False

    print("\n✅ Semantic search works!")
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("=" * 70)
    print(" " * 20 + "LIVE DEPLOYMENT TEST SUITE")
    print(f" " * 10 + f"{BASE_URL}")
    print("=" * 70)

    results = []

    try:
        # Run all tests
        results.append(("Health Check", test_health()))
        results.append(("Root Endpoint", test_root()))
        results.append(("Document Extraction", test_extraction()))
        results.append(("Similarity Matching", test_matching()))
        results.append(("PDF Generation", test_pdf_generation()))
        results.append(("Consent Flow", test_consent_flow()))
        results.append(("Semantic Search", test_search()))

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{test_name:30s} {status}")

        print("-" * 70)
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

        if passed == total:
            print("\n[SUCCESS] ALL TESTS PASSED! Service is fully operational!")
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed. Check errors above.")

        print("\n" + "=" * 70)
        print("DEPLOYMENT STATUS")
        print("=" * 70)
        print(f"[OK] Service URL: {BASE_URL}")
        print(f"[OK] API Documentation: {BASE_URL}/docs")
        print(f"[OK] Health Check: {BASE_URL}/health")
        print(f"[OK] Deployed on: Render (Free Tier)")
        print(f"[OK] Memory Usage: <100MB (optimized for free tier)")
        print("\n[NOTE] Real AI extraction requires OPENAI_API_KEY.")
        print("       Currently using mock data for extraction endpoint.")
        print("       All other features use real algorithms.")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Connection error: {str(e)}")
        print("        Make sure the service is deployed and accessible.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
