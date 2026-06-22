import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import create_telegram_app, WEBHOOK_URL
from bot.finance.handlers import cost_conv_handler
from bot.ai_handlers import ai_command, handle_photo, handle_ai_callback
from bot.project_report.handlers import task_command, report_command
from database.db import get_db_pool, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for db pool and bot application
db_pool = None
telegram_app = create_telegram_app()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    # Startup
    logger.info("Starting up database connection...")
    db_pool = await get_db_pool()
    await init_db(db_pool)
    
    # Initialize application
    logger.info("Initializing Telegram application...")
    await telegram_app.initialize()
    
    # Register handlers
    telegram_app.add_handler(cost_conv_handler)
    telegram_app.add_handler(CommandHandler("ai", ai_command))
    telegram_app.add_handler(CommandHandler("task", task_command))
    telegram_app.add_handler(CommandHandler("report", report_command))
    telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    telegram_app.add_handler(CallbackQueryHandler(handle_ai_callback, pattern="^ai_"))
    
    # Set webhook if URL is provided
    if WEBHOOK_URL:
        logger.info(f"Setting webhook to {WEBHOOK_URL}")
        await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    else:
        logger.warning("No WEBHOOK_URL provided. Webhook not set.")
    
    await telegram_app.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await telegram_app.stop()
    await telegram_app.shutdown()
    if db_pool:
        await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook updates from Telegram."""
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return Response(status_code=200)

@app.get("/ping")
async def ping():
    """Endpoint for UptimeRobot keep-alive."""
    return {"status": "ok", "message": "Bot is alive!"}

if __name__ == "__main__":
    import uvicorn
    # When running directly, use Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
