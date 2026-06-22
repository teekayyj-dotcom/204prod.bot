import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
import google.generativeai as genai

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

# We initialize the application without `run_polling()` since we use Webhooks.
def create_telegram_app():
    return ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
