# 🎮 Epic Games Freebies Discord Notifier

A lightweight, zero-cost, privacy-first automation tool that checks the Epic Games Store for weekly free games and sends rich embeds to your Discord server via Webhooks.

No third-party Discord bots, no server permissions required, and no persistent server hosting needed. Runs entirely on **GitHub Actions**.

---

## ✨ Features

- **Automated Scheduling:** Runs automatically every Thursday at 16:15 UTC (when Epic rotates weekly titles).
- **Manual Trigger Support:** Run on demand anytime from the GitHub Actions tab.
- **Rich Embeds:** Posts game artwork, summary descriptions, claim expiration dates, and direct store links.
- **Privacy-First:** Your Discord server remains completely private—only a standard incoming webhook URL is used.
- **100% Free:** Operates well within GitHub Actions' free runner allowance.

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── epic_freebies.yml   # Cron workflow & GitHub Actions runner
├── check_epic.py               # Python scraper & Discord webhook dispatcher
└── README.md                   # Documentation
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

### 3. Test the Automation
1. Go to the **Actions** tab at the top of your repository.
2. Select **Check Epic Games Freebies** from the left workflow menu.
3. Click the **Run workflow** dropdown on the right and click the green **Run workflow** button.
4. Once completed (green checkmark), check your Discord channel for the new freebie announcement!

---

## 🛠️ Local Development & Testing

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
2. Filters items where `discountPercentage == 0` and the current date falls between the promotion's start and end timestamps.
3. Formats an embed payload with the game's title, synopsis, promotional banner, and claim URL.
4. Dispatches the embed to the Discord channel using an HTTP `POST` request to the webhook URL.
