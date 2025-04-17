import logging
import requests
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import time

# 🔑 API Keys
GEMINI_API_KEY = "AIzaSyD7UMUb-eB4Skbe_BBVq5xiBH6F9-EfK34"
SERPAPI_API_KEY = "b4371c963da14cc7576b5b85a4cb0f4e65cf79d43f554c18b6548059918dccad"
TELEGRAM_BOT_TOKEN = "8073825732:AAHnbKry_UCnOSALIn92XhR49K3TSNOF1Ww"

genai.configure(api_key=GEMINI_API_KEY)

import time

def search_news_snippets(query, timeout=15, retries=2):
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "tbm": "nws",
        "q": query
    }

    for attempt in range(retries):
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            news_results = data.get("news_results", [])
            if not news_results:
                return "⚠️ No relevant articles found."

            snippets = []
            for res in news_results[:3]:
                title = res.get("title", "No title")
                snippet = res.get("snippet", "No summary")
                link = res.get("link", "")
                snippets.append(f"📰 {title}\n{snippet}\n🔗 {link}")

            return "\n\n".join(snippets)

        except requests.exceptions.Timeout:
            print(f"⏱️ Attempt {attempt+1} timed out. Retrying...")
            time.sleep(2)  # small wait before retrying

        except requests.exceptions.RequestException as e:
            return f"❌ Error fetching search results: {e}"

    return "❌ Search failed after multiple attempts. Try again later."


# 🤖 Gemini Fact Checker
def fact_check_claim_with_gemini(claim):
    news = search_news_snippets(claim)

    if "❌" in news or "⚠️" in news:
        return news

    prompt = f"""
You are a fact-checking assistant.

**Claim**: "{claim}"

Here are news articles:
{news}

Based on this, decide:
- ✅ TRUE
- ❌ FALSE
- ⚠️ UNCERTAIN

Explain in 2–3 lines.
    """

    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"❌ Gemini error: {e}"

# 🛠️ Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to FactCheckBot!\nSend me any news claim, and I'll tell you if it's likely ✅ true, ❌ false, or ⚠️ uncertain using real news and AI."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    claim = update.message.text
    await update.message.reply_text("🔍 Fact-checking your claim. Please wait...")
    result = fact_check_claim_with_gemini(claim)
    await update.message.reply_text(result)

# 🚀 Run the Bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running. Press Ctrl+C to stop.")
    app.run_polling()