"""
Complete example demonstrating all API features
"""
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time


BASE_URL = "http://localhost:8000"


def create_sample_license():
    """Create a sample driver's license image with text"""
    # Create a simple driver's license mockup
    img = Image.new("RGB", (800, 500), color="#E8F4F8")
    draw = ImageDraw.Draw(img)

    # Title
    draw.rectangle([0, 0, 800, 60], fill="#2C3E50")
    draw.text((250, 15), "DRIVER LICENSE", fill="white")

    # Fields
    y_pos = 100
    fields = [
        ("Name:", "JOHN DOE"),
        ("DOB:", "01/15/1990"),
        ("Address:", "123 MAIN STREET, SAN JOSE CA 95110"),
        ("License #:", "DL12345678"),
        ("Expiry:", "01/15/2028"),
    ]

    for label, value in fields:
        draw.text((50, y_pos), label, fill="black")
        draw.text((250, y_pos), value, fill="black")
        y_pos += 50

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes


def demo_complete_workflow():
    """
    Demonstrate a complete workflow:
    1. Extract PII from document
    2. Store embeddings
    3. Match against stored data
    4. Generate pre-filled PDF
    5. Create and redeem consent token
    6. Search for profiles
    """

    print("=" * 70)
    print("COMPLETE PII EXTRACTION SERVICE DEMO")
    print("=" * 70)

    # Step 1: Extract PII from document
    print("\n📄 STEP 1: Extracting PII from document...")
    print("-" * 70)

    img_bytes = create_sample_license()

    files = {"file": ("driver_license.png", img_bytes, "image/png")}
    data = {"profile_id": "demo_user_001", "document_type": "driver_license"}

    response = requests.post(f"{BASE_URL}/extract", files=files, data=data)

    if response.status_code != 200:
        print(f"❌ Extraction failed: {response.text}")
        return

    extraction_result = response.json()
    print("✅ Extraction successful!")
    print(f"\nProfile ID: {extraction_result['profile_id']}")
    print(f"Document Type: {extraction_result['document_type']}")
    print("\nExtracted Fields:")

    extracted_fields = {}
    for field_name, field_data in extraction_result["fields"].items():
        value = field_data["value"]
        confidence = field_data["confidence"]
        extracted_fields[field_name] = value
        print(f"  • {field_name:15s}: {value or 'N/A':30s} (confidence: {confidence:.2%})")

    # Step 2: Match PII (exact match)
    print("\n\n🔍 STEP 2: Matching PII (Exact Match)...")
    print("-" * 70)

    match_data = {
        "profile_id": "demo_user_001",
        "full_name": extracted_fields.get("full_name", "John Doe"),
        "address": extracted_fields.get(
            "address", "123 Main Street, San Jose CA 95110"
        ),
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data)

    if response.status_code == 200:
        match_result = response.json()
        print("✅ Match completed!")
        print(f"\n  Name Similarity:    {match_result['name_similarity']:.1%}")
        print(f"  Address Similarity: {match_result['address_similarity']:.1%}")
        print(f"  Overall Score:      {match_result['overall_score']:.1%}")
        print(f"  Classification:     {match_result['classification'].upper()}")

    # Step 3: Match PII (slight variation)
    print("\n\n🔍 STEP 3: Matching PII (Slight Variation)...")
    print("-" * 70)

    match_data_variant = {
        "profile_id": "demo_user_001",
        "full_name": "John David Doe",  # Middle name added
        "address": "123 Main St, San Jose CA",  # Abbreviated
    }

    response = requests.post(f"{BASE_URL}/match", json=match_data_variant)

    if response.status_code == 200:
        match_result = response.json()
        print("✅ Match completed!")
        print(f"\n  Name Similarity:    {match_result['name_similarity']:.1%}")
        print(f"  Address Similarity: {match_result['address_similarity']:.1%}")
        print(f"  Overall Score:      {match_result['overall_score']:.1%}")
        print(f"  Classification:     {match_result['classification'].upper()}")

    # Step 4: Generate pre-filled PDF
    print("\n\n📋 STEP 4: Generating Pre-filled PDF...")
    print("-" * 70)

    pdf_data = {
        "form_type": "sample_form",
        "fields": {
            "full_name": extracted_fields.get("full_name", "N/A"),
            "dob": extracted_fields.get("date_of_birth", "N/A"),
            "address": extracted_fields.get("address", "N/A"),
            "id_number": extracted_fields.get("id_number", "N/A"),
            "expiry_date": extracted_fields.get("expiry_date", "N/A"),
        },
    }

    response = requests.post(f"{BASE_URL}/prefill-pdf", json=pdf_data)

    if response.status_code == 200:
        output_file = "demo_filled_form.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF generated successfully!")
        print(f"   Saved to: {output_file}")
        print(f"   File size: {len(response.content):,} bytes")

    # Step 5: Create consent token
    print("\n\n🔐 STEP 5: Creating Consent Token...")
    print("-" * 70)

    consent_data = {
        "profile_id": "demo_user_001",
        "fields_allowed": ["full_name", "dob", "address"],
    }

    response = requests.post(f"{BASE_URL}/consent/create", json=consent_data)

    if response.status_code == 200:
        consent_result = response.json()
        token = consent_result["token"]
        expires_at = consent_result["expires_at"]

        print("✅ Consent token created!")
        print(f"   Token (truncated): {token[:60]}...")
        print(f"   Expires at: {expires_at}")
        print(f"   Allowed fields: {', '.join(consent_data['fields_allowed'])}")

        # Step 6: Redeem consent token
        print("\n\n🔓 STEP 6: Redeeming Consent Token...")
        print("-" * 70)

        response = requests.get(f"{BASE_URL}/consent/redeem", params={"token": token})

        if response.status_code == 200:
            allowed_data = response.json()
            print("✅ Token redeemed successfully!")
            print("\nRetrieved fields (only allowed ones):")
            for field_name, field_value in allowed_data.items():
                print(f"  • {field_name:15s}: {field_value}")

    # Step 7: Semantic search
    print("\n\n🔎 STEP 7: Semantic Search...")
    print("-" * 70)

    search_queries = [
        "John",  # Full match
        "Doe",  # Last name
        "Main Street",  # Address search
        "San Jose",  # City search
    ]

    for query in search_queries:
        response = requests.get(f"{BASE_URL}/search", params={"query": query, "limit": 3})

        if response.status_code == 200:
            search_result = response.json()
            print(f"\n  Query: '{query}'")
            print(f"  Results: {len(search_result['results'])} found")

            for i, result in enumerate(search_result["results"], 1):
                print(f"\n    {i}. {result['full_name']}")
                print(f"       Address: {result['address']}")
                print(f"       Similarity: {result['similarity_score']:.1%}")

    # Final summary
    print("\n\n" + "=" * 70)
    print("DEMO COMPLETED SUCCESSFULLY! ✨")
    print("=" * 70)
    print("\nKey features demonstrated:")
    print("  ✓ Document PII extraction with AI")
    print("  ✓ Automatic data normalization")
    print("  ✓ Embedding-based similarity matching")
    print("  ✓ PDF form generation")
    print("  ✓ Secure consent-based sharing")
    print("  ✓ Semantic search")
    print("\nGenerated files:")
    print("  • demo_filled_form.pdf")
    print("\n")


if __name__ == "__main__":
    try:
        demo_complete_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Start it with: python app/main.py\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
