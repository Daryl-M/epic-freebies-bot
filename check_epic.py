import os
from datetime import datetime, timezone
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing.")

API_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-GB&country=GB&allowCountries=GB"

response = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
response.raise_for_status()
data = response.json()

elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
now = datetime.now(timezone.utc)

for item in elements:
    title = item.get("title")
    description = item.get("description", "No description provided.")
    promotions = item.get("promotions") or {}
    promotional_offers = promotions.get("promotionalOffers", [])

    is_free_now = False
    end_date_str = ""

    if promotional_offers:
        offers = promotional_offers[0].get("promotionalOffers", [])
        for offer in offers:
            start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
            discount = offer.get("discountSetting", {}).get("discountPercentage", -1)

            # Must be currently running and 100% off
            if start <= now <= end and discount == 0:
                is_free_now = True
                end_date_str = offer.get("endDate", "")[:10]
                break

    if is_free_now:
        # Determine product store URL
        slug = (
            item.get("productSlug")
            or (item.get("offerMappings", [{}])[0].get("pageSlug") if item.get("offerMappings") else None)
            or (item.get("catalogNs", {}).get("mappings", [{}])[0].get("pageSlug") if item.get("catalogNs", {}).get("mappings") else None)
        )
        game_url = f"https://store.epicgames.com/p/{slug}" if slug else "https://store.epicgames.com/free-games"

        # Extract wide cover image
        key_images = item.get("keyImages", [])
        image_url = next(
            (img["url"] for img in key_images if img.get("type") in ["OfferImageWide", "DieselStoreFrontWide"]),
            key_images[0]["url"] if key_images else None,
        )

        # Build Discord Embed
        payload = {
            "embeds": [{
                "title": f"🎮 Free Game on Epic: {title}",
                "description": description[:350] + ("..." if len(description) > 350 else ""),
                "url": game_url,
                "color": 3447003,  # Discord blurple
                "image": {"url": image_url} if image_url else {},
                "fields": [
                    {"name": "Price", "value": "~~100% Free~~", "inline": True},
                    {"name": "Claim Before", "value": end_date_str if end_date_str else "Next Rotation", "inline": True},
                ],
                "footer": {"text": "Epic Games Weekly Drop"}
            }]
        }
        
        req = requests.post(WEBHOOK_URL, json=payload)
        req.raise_for_status()
