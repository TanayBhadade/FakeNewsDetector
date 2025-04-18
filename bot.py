# 🌐 Flask server to keep Replit awake
from flask import Flask
from threading import Thread

app = Flask("")

@app.route('/')
def home():
    return "✅ Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_web).start()

# 🔧 Imports
import os
import time
import requests
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Environment Variables
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# 🔑 Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

# 🔎 News Search (SerpAPI with Retry)
def search_news_snippets(query):
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "tbm": "nws",
        "q": query
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = response.json()

        results = data.get("news_results", [])
        if not results:
            return "⚠️ No relevant articles found."

        snippets = []
        for res in results[:3]:
            title = res.get("title", "No title")
            snippet = res.get("snippet", "No summary")
            link = res.get("link", "")
            snippets.append(f"📰 {title}\n{snippet}\n🔗 {link}")

        return "\n\n".join(snippets)

    except requests.exceptions.Timeout:
        time.sleep(3)
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=20)
            data = response.json()
            results = data.get("news_results", [])
            if not results:
                return "⚠️ No relevant articles found."

            snippets = []
            for res in results[:3]:
                title = res.get("title", "No title")
                snippet = res.get("snippet", "No summary")
                link = res.get("link", "")
                snippets.append(f"📰 {title}\n{snippet}\n🔗 {link}")

            return "\n\n".join(snippets)

        except Exception as e:
            return f"❌ Search retry failed. Check your internet or API quota. (Error: {e})"

    except Exception as e:
        return f"❌ Could not fetch news from SerpAPI. Please try again later.\n(Error: {e})"

# 🤖 Gemini-Based Fact Checking
prompt = f"""
You are an intelligent fact-checking assistant.

Your task is to assess the truthfulness of the following claim by analyzing supporting or contradictory information from recent news articles.

Claim:
"{claim}"

News Articles:
{news}

Based on this information, classify the claim as one of the following:
✅ TRUE – if the articles clearly support it  
❌ FALSE – if the articles contradict it  
⚠️ UNCERTAIN – if the articles are inconclusive or mixed

Provide a short 2-line explanation and cite at least one article title or link in your reasoning.
Be neutral and concise.
"""




    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini error: {e}"

# 🤖 Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send a news claim and I'll fact-check it for you!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    claim = update.message.text
    await update.message.reply_text("🔍 Fact-checking your claim...")
    result = fact_check_claim_with_gemini(claim)
    await update.message.reply_text(result)

# 🚀 Start the Bot
if __name__ == "__main__":
    app_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()
