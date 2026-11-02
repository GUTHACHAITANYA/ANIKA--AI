"""
Product variant matching for Smart Buy.

Ensures products being compared are actually equivalent.
A 128GB variant must not be compared with a 256GB variant.
"""
import re
from typing import List, Tuple


# Attributes that define a distinct variant
_VARIANT_KEYS = ["storage", "ram", "color", "screen_size", "size"]


def extract_variant_attributes(product_title: str) -> dict:
    """
    Extract variant-defining attributes from a product title string.
    Returns a dict of {attribute: normalised_value}.
    """
    title_lower = product_title.lower()
    attrs = {}

    # RAM: e.g. "8GB RAM", "16 GB"
    ram_match = re.search(r"(\d+)\s*gb\s+ram", title_lower)
    if ram_match:
        attrs["ram"] = f"{ram_match.group(1)}GB"

    # Storage: e.g. "256GB", "512 GB", "1TB"
    storage_match = re.search(r"(\d+)\s*(tb|gb)\b", title_lower)
    if storage_match and "ram" not in title_lower[max(0, storage_match.start()-5):storage_match.start()+10]:
        unit = storage_match.group(2).upper()
        val = int(storage_match.group(1))
        attrs["storage"] = f"{val}{unit}"

    # Color keywords
    colors = ["black", "white", "blue", "red", "green", "yellow", "pink", "gold",
              "silver", "grey", "gray", "purple", "orange", "titanium", "midnight",
              "starlight", "graphite", "phantom", "obsidian", "coral"]
    for color in colors:
        if color in title_lower:
            attrs["color"] = color.title()
            break

    # Screen size: e.g. "55 inch", "6.7-inch"
    size_match = re.search(r'(\d+\.?\d*)\s*[\-–]?\s*inch', title_lower)
    if size_match:
        attrs["screen_size"] = f"{size_match.group(1)} inch"

    return attrs


def variants_are_compatible(attrs_a: dict, attrs_b: dict) -> Tuple[bool, List[str]]:
    """
    Check whether two offer's variant attribute dicts are compatible
    (i.e. they represent the same product variant).

    Returns (is_compatible, list_of_mismatched_keys).
    If a key is missing from one dict, it is ignored (ambiguous).
    """
    mismatches = []
    for key in _VARIANT_KEYS:
        val_a = attrs_a.get(key)
        val_b = attrs_b.get(key)
        if val_a and val_b and val_a.lower() != val_b.lower():
            mismatches.append(key)
    return len(mismatches) == 0, mismatches


def match_offers_to_groups(offers: List[dict]) -> List[dict]:
    """
    Group offers by variant compatibility and annotate each offer with:
      - variant_attributes (extracted from title if missing)
      - variant_warning: list of attribute differences from the top result
    """
    if not offers:
        return offers

    # Extract attributes for each offer
    for offer in offers:
        if not offer.get("variant_attributes"):
            offer["variant_attributes"] = extract_variant_attributes(
                offer.get("product_title", "")
            )

    # Use the first (highest-discount) offer as reference
    ref_attrs = offers[0].get("variant_attributes", {})

    for offer in offers:
        _, mismatches = variants_are_compatible(ref_attrs, offer.get("variant_attributes", {}))
        offer["variant_warning"] = mismatches

    return offers

