"""
Data normalization utilities
"""
import re
from datetime import datetime
from typing import Optional


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format

    Args:
        date_str: Date in various formats

    Returns:
        Date in YYYY-MM-DD format or None if parsing fails
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Common date formats to try
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def normalize_name(name: Optional[str]) -> Optional[str]:
    """
    Normalize name to consistent casing

    Args:
        name: Full name string

    Returns:
        Normalized name in Title Case
    """
    if not name:
        return None

    # Remove extra whitespace
    name = " ".join(name.split())

    # Title case for most names
    # Handle special cases like "McDonald", "O'Brien" properly
    name = name.title()

    return name


def normalize_address(address: Optional[str]) -> Optional[str]:
    """
    Normalize address by cleaning and standardizing format

    Args:
        address: Address string

    Returns:
        Cleaned and normalized address
    """
    if not address:
        return None

    # Remove extra whitespace
    address = " ".join(address.split())

    # Standardize common abbreviations
    replacements = {
        r"\bSt\.?\b": "Street",
        r"\bAve\.?\b": "Avenue",
        r"\bRd\.?\b": "Road",
        r"\bBlvd\.?\b": "Boulevard",
        r"\bDr\.?\b": "Drive",
        r"\bLn\.?\b": "Lane",
        r"\bCt\.?\b": "Court",
        r"\bPl\.?\b": "Place",
        r"\bApt\.?\b": "Apartment",
        r"\bSte\.?\b": "Suite",
    }

    for pattern, replacement in replacements.items():
        address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)

    return address


def normalize_id_number(id_num: Optional[str]) -> Optional[str]:
    """
    Normalize ID number by removing special characters

    Args:
        id_num: ID number string

    Returns:
        Cleaned ID number (alphanumeric only)
    """
    if not id_num:
        return None

    # Remove all non-alphanumeric characters
    normalized = re.sub(r"[^A-Za-z0-9]", "", id_num)

    return normalized.upper()
