from core.logger import setup_logger
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from core.config import BOT_TOKEN, LOCAL_API_URL
from handlers import setup_handlers

logger = setup_logger("my_bot")

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables.")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

    builder = Application.builder().token(BOT_TOKEN)

    # If a local API URL is provided, set it in the builder
    if LOCAL_API_URL:
        logger.info(f"Using local API URL: {LOCAL_API_URL}")
        builder = builder.base_url(f"{LOCAL_API_URL}/bot").base_file_url(f"{LOCAL_API_URL}/file/bot")

    app = builder.build()
    
    # Register handlers
    setup_handlers(app)

    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()