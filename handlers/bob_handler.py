from core.logger import setup_logger
from core.config import TIMEZONE
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import datetime
from zoneinfo import ZoneInfo

logger = setup_logger(f"my_bot.{__name__}")

async def bob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert update.effective_user is not None

    logger.info(f"User {update.effective_user.id} use the bob command.")
    
    current_time = datetime.now(ZoneInfo(TIMEZONE)).strftime("%H")

    logger.debug(f"Current bot time: {current_time}")

    try:
        # From 10 PM to 5 AM, send sleepy Bob image
        if int(current_time) >= 22 or int(current_time) < 5:
            with open("resources/sleepy_bob_image.png", "rb") as image_file:
                await update.message.reply_photo(photo=image_file, caption="It's quite late! Bob is probably sleeping right now. 😴")
        else:
            with open("resources/bob_image.png", "rb") as image_file:
                await update.message.reply_photo(photo=image_file, caption="Here's Bob for you! 😃")
    except FileNotFoundError:
        logger.error("Bob image file not found.")
        await update.message.reply_text("Sorry, I couldn't find where is the Bob image right now :(")
    

bob_handler = CommandHandler("bob", bob)