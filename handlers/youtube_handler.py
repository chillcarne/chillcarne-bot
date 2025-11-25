from core.logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters, CallbackContext, CallbackQueryHandler
from decorators.subscription_required import subscription_required
from services.youtube_service import get_youtube_video_info, download_preview, download_video
import os

logger = setup_logger(f"my_bot.{__name__}")

TELEGRAM_TIMEOUT = 300  # seconds
TELEGRAM_LIMIT_MB = 2000  # 2GB
MB_DIVISOR = 1024 * 1024

def _build_video_info_markup(video_info: dict) -> tuple[str, InlineKeyboardMarkup]:
    metadata = video_info.get('metadata', {})
    text = f"{metadata.get('title', 'No Title')}\n\n"
    text += f"Channel: {metadata.get('channel', 'Unknown')}\n"
    keyboard = [
        [InlineKeyboardButton("📺 Video + Audio", callback_data="yt_combined_details")],
        [InlineKeyboardButton("🎥 Video Only", callback_data="yt_video_details")],
        [InlineKeyboardButton("🎵 Audio Only", callback_data="yt_audio_bitrates")],
    ]
    return text, InlineKeyboardMarkup(keyboard)

@subscription_required
async def download_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert context.user_data is not None
    assert update.effective_chat is not None

    status_message = await update.message.reply_text("⏳ Retrieving video information...")

    url = update.message.text
    video_info = get_youtube_video_info(url)

    if not video_info:
        await status_message.edit_text("❌ Failed to retrieve video information.")
        return
    
    context.user_data[update.effective_chat.id] = {
        'video_info': video_info,
        'url': url
    }

    text, reply_markup = _build_video_info_markup(video_info)
    preview_url = video_info.get('metadata', {}).get('thumbnail')
    preview_path = download_preview(preview_url)

    if preview_path:
        with open(preview_path, "rb") as preview_file:
            await update.message.reply_photo(photo=preview_file, caption=text, reply_markup=reply_markup)
            os.remove(preview_path)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

    await status_message.delete()

# Button click handler
@subscription_required
async def back_to_previous_options_handler(update: Update, context: CallbackContext) -> None:
    assert update.callback_query is not None
    assert update.callback_query.data is not None
    assert update.callback_query.message is not None
    assert context.user_data is not None

    await update.callback_query.answer()  # Подтверждаем обработку callback
    
    chat_id = update.callback_query.message.chat.id
    user_data = context.user_data.get(chat_id, {})

    if not user_data:
        await update.callback_query.edit_message_caption("❌ Session expired. Please send the URL again.")
        return

    video_info = user_data['video_info']
    text, reply_markup = _build_video_info_markup(video_info)
    await update.callback_query.edit_message_caption(text, reply_markup=reply_markup)

# Button click handler
@subscription_required
async def show_available_formats_callback_handler(update: Update, context: CallbackContext) -> None:
    assert update.callback_query is not None
    assert update.callback_query.data is not None
    assert update.callback_query.message is not None
    assert context.user_data is not None

    await update.callback_query.answer()  # Подтверждаем обработку callback
    
    chat_id = update.callback_query.message.chat.id
    user_data = context.user_data.get(chat_id, {})

    if not user_data:
        await update.callback_query.edit_message_caption("❌ Session expired. Please send the URL again.")
        return

    video_info = user_data['video_info']
    type_map = {
        "yt_combined_details": (video_info['combined_details'], "📺", ".mp4"),
        "yt_video_details": (video_info['video_details'], "🎥", ".mp4"),
        "yt_audio_bitrates": (video_info['audio_bitrates'], "🎵", ".m4a"),
    }

    if update.callback_query.data in type_map:
        fmt_list, emoji, ext = type_map[update.callback_query.data]
        keyboard = [
            [InlineKeyboardButton(f"{emoji} {ext} ({fmt[0]})", callback_data=f"download_youtube:{fmt[1]['format_id']}")]
            for fmt in fmt_list
        ] + [
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_previous_options")]
        ]
        await update.callback_query.edit_message_caption("Choose resolution:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_caption("❌ Unknown option selected. Please try again.")

    pass

# Button click handler
@subscription_required
async def download_video_callback_handler(update: Update, context: CallbackContext) -> None:
    assert update.callback_query is not None
    assert update.callback_query.data is not None
    assert update.callback_query.message is not None
    assert context.user_data is not None

    await update.callback_query.answer()  # Подтверждаем обработку callback

    chat_id = update.callback_query.message.chat.id
    user_data = context.user_data.get(chat_id, {})

    if not user_data:
        await update.callback_query.edit_message_caption("❌ Session expired. Please send the URL again.")
        return

    video_info = user_data['video_info']
    url = user_data['url']

    if update.callback_query.data.startswith("download_youtube:"):
        format_id = update.callback_query.data.split(":")[1]
    else:
        # Unknown callback data, should not happen
        logger.error("Unknown callback data received. Should not happen. Check the handler patterns.")
        await update.callback_query.edit_message_caption("❌ Unknown option selected. Please try again.")
        return

    status_message = await update.callback_query.edit_message_caption("⏳ Downloading...")
    media_path = download_video(url, format_id)

    if os.path.getsize(media_path) / MB_DIVISOR > TELEGRAM_LIMIT_MB:
        text = "❌ File too large to send via Telegram."
        text+= f"\n\nThe downloaded file exceeds Telegram's size limit of {TELEGRAM_LIMIT_MB//1024}GB."
        text+= "\nPlease try downloading a lower resolution."
        
        await update.callback_query.edit_message_caption(text)
        os.remove(media_path)
        return
    
    timeout_params = {
        'read_timeout': TELEGRAM_TIMEOUT,
        'write_timeout': TELEGRAM_TIMEOUT,
        'connect_timeout': TELEGRAM_TIMEOUT
    }

    try:
        with open(media_path, 'rb') as media_file:
            text = f"✅ Download complete: {video_info['metadata'].get('title', 'No Title')}"

            if media_path.endswith('.m4a'):
                await update.callback_query.edit_message_caption("⏳ Sending audio...")
                await context.bot.send_audio(chat_id=chat_id, audio=media_file, filename=os.path.basename(media_path), caption=text, **timeout_params)
            else:
                await update.callback_query.edit_message_caption("⏳ Sending video...")
                await context.bot.send_video(chat_id=chat_id, video=media_file, filename=os.path.basename(media_path), supports_streaming=True, caption=text, **timeout_params)
            
            await status_message.delete()  # type: ignore
    except Exception as e:
        logger.error(f"Error sending YouTube video/audio: {e}")
        await update.callback_query.edit_message_caption("❌ Error sending file.")
    finally:
        os.remove(media_path)

youtube_filter = filters.TEXT & filters.Regex(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/')

youtube_handler = MessageHandler(youtube_filter, download_youtube)
show_available_formats_callback = CallbackQueryHandler(show_available_formats_callback_handler, pattern=r'^yt_')
download_video_handler_callback = CallbackQueryHandler(download_video_callback_handler, pattern=r'^download_youtube:')
back_to_previous_options_handler_callback = CallbackQueryHandler(back_to_previous_options_handler, pattern=r'^back_to_previous_options$')