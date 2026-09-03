"""
LEVELLY — Payment Category Normalization Engine
Maps merchant information, descriptions, and user categories into
standardized financial categories for Save-at-Pay policy evaluation.
"""
from typing import Optional, Dict, Any


class CategoryService:
    """
    Normalizes diverse merchant names, MCC/tags, and user inputs
    into canonical LEVELLY categories.
    """

    MAPPING = {
        # Food & Dining
        "food": "food",
        "food & grocery": "food",
        "grocery": "food",
        "supermarket": "food",
        "restaurant": "food",
        "cafe": "food",
        "swiggy": "food",
        "zomato": "food",
        "dining": "food",

        # Fuel & Commute
        "fuel": "fuel",
        "petrol": "fuel",
        "diesel": "fuel",
        "gas": "fuel",
        "petrol station": "fuel",
        "fuel station": "fuel",
        "cng": "fuel",
        "indian oil": "fuel",
        "bharat petroleum": "fuel",
        "hpcl": "fuel",

        # Vehicle & Maintenance
        "vehicle": "vehicle",
        "vehicle repair": "vehicle",
        "bike repair": "vehicle",
        "service center": "vehicle",
        "mechanic": "vehicle",
        "auto parts": "vehicle",
        "tyre": "vehicle",

        # Healthcare & Wellness
        "healthcare": "healthcare",
        "pharmacy": "healthcare",
        "medical": "healthcare",
        "clinic": "healthcare",
        "hospital": "healthcare",
        "medicine": "healthcare",
        "apollo": "healthcare",
        "medplus": "healthcare",

        # Education
        "education": "education",
        "school": "education",
        "college": "education",
        "tuition": "education",
        "books": "education",
        "fees": "education",

        # Entertainment
        "entertainment": "entertainment",
        "movie": "entertainment",
        "cinema": "entertainment",
        "ott": "entertainment",
        "gaming": "entertainment",

        # Shopping
        "shopping": "shopping",
        "clothing": "shopping",
        "retail": "shopping",
        "electronics": "shopping",

        # Family & Remittances
        "family": "family",
        "home": "family",
        "remittance": "family",

        # Bills & Utilities (Usually fixed, 0% base save)
        "bills": "bills",
        "electricity": "bills",
        "water": "bills",
        "recharge": "bills",
        "mobile recharge": "bills",
        "rent": "rent",
    }

    @classmethod
    def normalize(
        cls,
        merchant_name: Optional[str] = None,
        merchant_category: Optional[str] = None,
        user_category: Optional[str] = None,
    ) -> str:
        """
        Determine canonical category using priority:
        1. Explicit user-selected category (if valid)
        2. Merchant category metadata
        3. Keyword matching on merchant name
        4. Default to 'other'
        """
        # 1. User category
        if user_category:
            normalized = cls.MAPPING.get(user_category.strip().lower())
            if normalized:
                return normalized

        # 2. Merchant category
        if merchant_category:
            normalized = cls.MAPPING.get(merchant_category.strip().lower())
            if normalized:
                return normalized

        # 3. Keyword matching on merchant name
        if merchant_name:
            name_lower = merchant_name.strip().lower()
            for key, canonical in cls.MAPPING.items():
                if key in name_lower:
                    return canonical

        return "other"
