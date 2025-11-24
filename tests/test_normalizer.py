"""
Tests for normalization utilities
"""
import pytest
from app.utils.normalizer import (
    normalize_date,
    normalize_name,
    normalize_address,
    normalize_id_number,
)


class TestDateNormalization:
    """Tests for date normalization"""

    def test_normalize_date_yyyy_mm_dd(self):
        assert normalize_date("2024-01-15") == "2024-01-15"

    def test_normalize_date_mm_dd_yyyy(self):
        assert normalize_date("01/15/2024") == "2024-01-15"

    def test_normalize_date_dd_mm_yyyy(self):
        assert normalize_date("15/01/2024") == "2024-01-15"

    def test_normalize_date_with_month_name(self):
        assert normalize_date("January 15, 2024") == "2024-01-15"

    def test_normalize_date_invalid(self):
        assert normalize_date("invalid date") is None

    def test_normalize_date_empty(self):
        assert normalize_date("") is None

    def test_normalize_date_none(self):
        assert normalize_date(None) is None


class TestNameNormalization:
    """Tests for name normalization"""

    def test_normalize_name_lowercase(self):
        assert normalize_name("john doe") == "John Doe"

    def test_normalize_name_uppercase(self):
        assert normalize_name("JOHN DOE") == "John Doe"

    def test_normalize_name_mixed(self):
        assert normalize_name("JoHn DoE") == "John Doe"

    def test_normalize_name_extra_spaces(self):
        assert normalize_name("  John   Doe  ") == "John Doe"

    def test_normalize_name_empty(self):
        assert normalize_name("") is None

    def test_normalize_name_none(self):
        assert normalize_name(None) is None


class TestAddressNormalization:
    """Tests for address normalization"""

    def test_normalize_address_abbreviations(self):
        result = normalize_address("123 Main St. Apt. 4B")
        assert "Street" in result
        assert "Apartment" in result

    def test_normalize_address_extra_spaces(self):
        result = normalize_address("  123   Main   Street  ")
        assert result == "123 Main Street"

    def test_normalize_address_empty(self):
        assert normalize_address("") is None

    def test_normalize_address_none(self):
        assert normalize_address(None) is None


class TestIdNumberNormalization:
    """Tests for ID number normalization"""

    def test_normalize_id_number_with_dashes(self):
        assert normalize_id_number("DL-123-456-78") == "DL12345678"

    def test_normalize_id_number_with_spaces(self):
        assert normalize_id_number("DL 123 456 78") == "DL12345678"

    def test_normalize_id_number_lowercase(self):
        assert normalize_id_number("dl12345678") == "DL12345678"

    def test_normalize_id_number_empty(self):
        assert normalize_id_number("") is None

    def test_normalize_id_number_none(self):
        assert normalize_id_number(None) is None
