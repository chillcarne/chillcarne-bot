from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from core.config import REQUIRED_CHANNEL_USERNAME

async def _is_subscribed(bot, user_id) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=f"@{REQUIRED_CHANNEL_USERNAME}", user_id=user_id)
        return member.status != 'left' and member.status != 'kicked' # Check if user is not left or kicked
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

async def _send_subscription_required_message(update: Update):
    assert update.message is not None

    text = f"❌ To use this bot, you need to subscribe to the channel @{REQUIRED_CHANNEL_USERNAME}.\n\n"
    text += "After subscribing, please try again."

    keyboard = [[InlineKeyboardButton(f"Subscribe to @{REQUIRED_CHANNEL_USERNAME.lstrip('@')}", url=f"https://t.me/{REQUIRED_CHANNEL_USERNAME.lstrip('@')}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)    

def subscription_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        assert update.effective_user is not None
        is_subscribed = await _is_subscribed(context.bot, update.effective_user.id)

        if is_subscribed:
            return await func(update, context)
        else:
            await _send_subscription_required_message(update)
    return wrapper