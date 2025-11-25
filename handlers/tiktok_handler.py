from core.logger import setup_logger
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from decorators.subscription_required import subscription_required
from services.tiktok_service import download_tiktok_video, get_tiktok_metadata
import os

logger = setup_logger(f"my_bot.{__name__}")

TELEGRAM_TIMEOUT = 300  # seconds

@subscription_required
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert update.message.text is not None
    assert update.effective_user is not None

    logger.info(f"User {update.effective_user.id} uses tiktok downloader command.")

    # Get metadata
    status_message = await update.message.reply_text("⏳ Preparing download...")

    tiktok_metadata = get_tiktok_metadata(update.message.text)

    text = "⬇️ Downloading TikTok video...\n\n"
    text+= f"Title: {tiktok_metadata.get('title', 'N/A')}"
    text+= f"\nDescription: {tiktok_metadata.get('desc', 'N/A')}"    
    await status_message.edit_text(text)

    # Download video
    video_path = download_tiktok_video(update.message.text)

    timeout_params = {
        'read_timeout': TELEGRAM_TIMEOUT,
        'write_timeout': TELEGRAM_TIMEOUT,
        'connect_timeout': TELEGRAM_TIMEOUT
    }

    try:
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, supports_streaming=True, **timeout_params) # type: ignore[attr-defined]

        await status_message.delete()
    except Exception as e:
        logger.error(f"Error sending TikTok video: {e}")
        await status_message.edit_text("❌ Error sending file.")
    finally:
        os.remove(video_path)

tiktok_filter = filters.TEXT & filters.Regex(r'(https?://)?(www\.)?(tiktok\.com|vt\.tiktok\.com)/')
tiktok_handler = MessageHandler(tiktok_filter, download_tiktok)
