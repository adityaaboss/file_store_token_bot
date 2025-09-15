# 📦 File Store Token Verification Bot

A Telegram bot to **store files** in a database and generate **time-limited token links** (valid for 12 hours by default).  
Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and MongoDB, deployable on **Render**.

---

## ✨ Features
- Upload any file (document, video, photo, audio) → get a tokenized download link.
- Tokens auto-expire after 12 hours (configurable).
- Files and tokens stored securely in MongoDB.
- Logging channel support.
- Render-ready (Webhook mode, no polling needed).

---

## 🛠 Deployment (Render)

### 1. Fork or Upload Repo
- Download this repo as `.zip` or fork it directly to your GitHub.
- Upload it to a **new GitHub repo**.

### 2. Create a Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Create **New Web Service**.
3. Connect your GitHub repo.
4. Use **Free Plan** (works fine for this bot).

### 3. Environment Variables
Add the following env vars in Render:

| Key            | Value (example)                                                                 |
|----------------|---------------------------------------------------------------------------------|
| `BOT_TOKEN`    | `` (your BotFather token)         |
| `OWNER_ID`     | `5494945309` (your Telegram user ID)                                            |
| `MONGO_URL`    | `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true`    |
| `DB_CHANNEL_ID`| `-1002865033508`                                                                |
| `LOG_CHANNEL_ID`| `-1002935516876`                                                               |
| `FILE_TTL_HOURS`| `12` (default expiry in hours)                                                 |
| `WEBHOOK_URL`  | `https://<your-app-name>.onrender.com/webhook`                                  |

### 4. Deploy 🚀
- Render will install dependencies (`requirements.txt`).
- It will run `Procfile` → start bot in webhook mode.
- Your bot is now live!

---

## 📂 Repo Structure
