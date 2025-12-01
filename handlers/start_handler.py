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

    text = "Hello! I'm chillcarne bot. 👋\n"
    text+= "\n"
    text+= "The bot can process several types of links and handle them automatically:\n"
    text+= "\n"
    text+= "• YouTube link — downloads YouTube or YouTube Shorts video. 🎬\n"
    text+= "• TikTok link — downloads TikTok video without watermark. 📱\n"
    text+= "• /bob — bob. 💁‍♂️\n"
    text+= "\n"
    text+= "Errors or unexpected issues may occasionally occur. When they happen, an automatic report is sent to me, so problems are detected and monitored without requiring manual feedback.\n"
    text+= "\n"
    text+= "Additionally, bug reports can be submitted manually on GitHub Issues page.\n"
    text+= "\n"
    text+= "The bot’s source code is open and available under the MIT license:\n"
    text+= "https://github.com/chillcarne/chillcarne_bot 📄\n"

    await update.message.reply_text(text)

start_handler = CommandHandler("start", start)