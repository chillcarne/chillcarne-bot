from core.logger import setup_logger
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from decorators.subscription_required import subscription_required

logger = setup_logger(f"my_bot.{__name__}")

@subscription_required
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert update.effective_user is not None

    logger.info(f"User {update.effective_user.id} started the bot.")
    
    await update.message.reply_text("Hello! I'm chillcarne bot.")

start_handler = CommandHandler("start", start)