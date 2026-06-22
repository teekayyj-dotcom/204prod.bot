import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import create_telegram_app
from bot.finance.handlers import cost_conv_handler
from bot.ai_handlers import ai_command, handle_photo, handle_ai_callback
from bot.project_report.handlers import task_command, report_command
from database.db import get_db_pool, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_init(app):
    """Initialize database when the bot starts polling."""
    logger.info("Starting up database connection...")
    pool = await get_db_pool()
    await init_db(pool)

def main():
    # Initialize application
    app = create_telegram_app()
    app.post_init = post_init
    
    # Register handlers
    app.add_handler(cost_conv_handler)
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("task", task_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_ai_callback, pattern="^ai_"))
    
    logger.info("Bot is starting in polling mode for local testing...")
    # drop_pending_updates ignores old messages sent while bot was offline
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
