# 🎮 Epic Games Freebies Discord Notifier

A lightweight, zero-cost, privacy-first automation tool that checks the Epic Games Store for free games and sends rich embeds to your Discord server via Webhooks.

Supports both standard **weekly giveaways** and **daily 24-hour event promotions** (e.g. holiday mystery drops). No third-party Discord bots, no server permissions required, and no persistent server hosting needed. Runs entirely on **GitHub Actions**.

---

## ✨ Features

- **Daily & Event Ready:** Runs automatically every day at 16:15 UTC, catching both weekly rotations and rapid 24-hour event drops.
- **Smart Deduplication:** Tracks individual promotional windows (`Title_EndDate`). Active offers are never spammed, but titles given away again in future promotions will still trigger alerts.
- **Rich Embeds:** Posts game artwork, summary descriptions, claim expiration dates, and direct store links.
- **Privacy-First:** Your Discord server remains completely private—only a standard incoming webhook URL is used.
- **100% Free:** Operates well within GitHub Actions' free runner allowance.

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── epic_freebies.yml    # Daily cron workflow & Git commit automation
├── check_epic.py                # Promotion scraper & Discord webhook dispatcher
├── posted_promotions.json       # Auto-generated cache tracking announced promos
└── README.md                    # Documentation
```

---

## 🚀 Setup Instructions

### 1. Create a Discord Webhook
1. In your Discord server, open **Server Settings** ➔ **Integrations** (or click the **⚙️ Settings** icon on the target channel ➔ **Integrations**).
2. Select **Webhooks** ➔ **New Webhook**.
3. Name your webhook (e.g., `Epic Freebies`) and select the destination channel.
4. Click **Copy Webhook URL**.

---

### 2. Configure GitHub Repository Secrets
1. In your GitHub repository, navigate to **Settings** (top navigation tab).
2. In the left sidebar, click **Secrets and variables** ➔ **Actions**.
3. Under **Repository secrets**, click **New repository secret**.
4. Set the fields:
   - **Name:** `DISCORD_WEBHOOK_URL`
   - **Secret:** Paste your Discord Webhook URL.
5. Click **Add secret**.

> **Note:** Ensure the secret is added under **Repository secrets** (not Environment secrets or Variables) and that there are no accidental spaces in the name.

---

### 3. Enable Workflow Permissions (Required for Cache)
Because the workflow automatically commits and saves `posted_promotions.json` back to your repo to prevent duplicate announcements:

1. In your GitHub repository, go to **Settings** ➔ **Actions** ➔ **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Click **Save**.

---

### 4. Test the Automation
1. Go to the **Actions** tab at the top of your repository.
2. Select **Check Epic Games Freebies** from the left workflow menu.
3. Click the **Run workflow** dropdown on the right and click the green **Run workflow** button.
4. Once completed, check your Discord channel for the announcements!

---

## 🛠️️ Local Development & Testing

To test or run the script locally on your machine:

```bash
# Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/epic-freebies-bot.git
cd epic-freebies-bot

# Install requirements
pip install requests

# Set your webhook URL (Linux / macOS)
export DISCORD_WEBHOOK_URL="[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)..."

# Set your webhook URL (Windows PowerShell)
$env:DISCORD_WEBHOOK_URL="[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)..."

# Run the check
python check_epic.py
```

---

## ⚙️ How It Works

1. Queries the official Epic Games Promotions API (`/freeGamesPromotions`).
2. Identifies active offers where `discountPercentage == 0` within current timestamp boundaries.
3. Compares each offer's unique fingerprint (`Title_EndDate`) against `posted_promotions.json`.
4. Sends Discord embeds for any unposted promotions and updates the cache file.
5. GitHub Actions commits the updated cache back to the repository with `[skip ci]`.
