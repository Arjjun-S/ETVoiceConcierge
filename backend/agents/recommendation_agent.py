import json
from pathlib import Path
from typing import Any

PRODUCTS_PATH = Path(__file__).resolve().parent.parent / "tools" / "et_products.json"

with PRODUCTS_PATH.open() as f:
    ET_PRODUCTS = json.load(f)


def _match_product(profile: dict[str, Any]) -> dict[str, Any]:
    experience = profile.get("experience", "beginner").lower()
    for product in ET_PRODUCTS:
        if product.get("type") == experience:
            return product
    return ET_PRODUCTS[0]


async def recommend(profile: dict[str, Any]) -> dict[str, Any]:
    product = _match_product(profile)
    return {
        "product": product,
        "message": f"I recommend {product['name']} based on your profile.",
    }
