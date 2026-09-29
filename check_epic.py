import os
import sys
import json
from datetime import datetime, timezone
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
CACHE_FILE = "posted_promotions.json"

if not WEBHOOK_URL:
    print("❌ ERROR: DISCORD_WEBHOOK_URL is missing or empty.", file=sys.stderr)
    sys.exit(1)

# Load existing promotion history
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            posted_promos = set(json.load(f))
    except Exception:
        posted_promos = set()
else:
    posted_promos = set()

API_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-GB&country=GB&allowCountries=GB"

print("🔍 Querying Epic Games Store API...")
try:
    response = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ Failed to reach Epic Games API: {e}", file=sys.stderr)
    sys.exit(1)

elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
now = datetime.now(timezone.utc)
new_posts = 0

for item in elements:
    title = item.get("title")
    promotions = item.get("promotions") or {}
    promotional_offers = promotions.get("promotionalOffers", [])

    is_free_now = False
    raw_end_date = ""

    if promotional_offers:
        for offer_group in promotional_offers:
            offers = offer_group.get("promotionalOffers", [])
            for offer in offers:
                try:
                    start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
                    discount = offer.get("discountSetting", {}).get("discountPercentage", -1)

                    if start <= now <= end and discount == 0:
                        is_free_now = True
                        raw_end_date = offer.get("endDate", "")
                        break
                except Exception:
                    continue
            if is_free_now:
                break

    if is_free_now and title and raw_end_date:
        # Unique fingerprint: Title + End Date of THIS specific giveaway
        promo_key = f"{title}_{raw_end_date}"

        if promo_key in posted_promos:
            print(f"⏭️ Skipping '{title}' (already announced for window ending {raw_end_date[:10]})")
            continue

        description = item.get("description") or "No description provided."
        slug = (
            item.get("productSlug")
            or (item.get("offerMappings", [{}])[0].get("pageSlug") if item.get("offerMappings") else None)
            or (item.get("catalogNs", {}).get("mappings", [{}])[0].get("pageSlug") if item.get("catalogNs", {}).get("mappings") else None)
            or item.get("urlSlug")
        )
        game_url = f"https://store.epicgames.com/p/{slug}" if slug else "https://store.epicgames.com/free-games"

        # Extract wide cover image
        key_images = item.get("keyImages", [])
        image_url = None
        for img in key_images:
            if img.get("type") in ["OfferImageWide", "DieselStoreFrontWide"]:
                image_url = img.get("url")
                break
        if not image_url and key_images:
            image_url = key_images[0].get("url")

        # Format readable end date
        end_date_str = raw_end_date[:10]

        embed = {
            "title": f"🎮 Free Game on Epic: {title}",
            "description": (description[:350] + "...") if len(description) > 350 else description,
            "url": game_url,
            "color": 3447003,
            "fields": [
                {"name": "Price", "value": "~~100% Free~~", "inline": True},
                {"name": "Claim Before", "value": end_date_str, "inline": True},
            ],
            "footer": {"text": "Epic Games Promotion"}
        }

        if image_url:
            embed["image"] = {"url": image_url}

        print(f"📤 Sending '{title}' to Discord...")
        try:
            req = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
            if req.ok:
                print(f"✅ Successfully posted '{title}'")
                posted_promos.add(promo_key)
                new_posts += 1
            else:
                print(f"❌ Discord error (HTTP {req.status_code}): {req.text}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Webhook request failed: {e}", file=sys.stderr)

# Save cache back to file
with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(sorted(list(posted_promos)), f, indent=2)

print(f"🏁 Finished. {new_posts} new announcement(s) sent.")
