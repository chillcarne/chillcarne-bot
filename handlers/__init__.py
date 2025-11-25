from telegram.ext import Application
from .start_handler import start_handler
from .error_handler import error_handler
from .youtube_handler import youtube_handler, show_available_formats_callback, download_video_handler_callback, back_to_previous_options_handler_callback

def setup_handlers(app: Application):
    # Start handler
    app.add_handler(start_handler)

    # Error handler
    app.add_error_handler(error_handler)

    # Youtube
    app.add_handler(youtube_handler)
    app.add_handler(show_available_formats_callback)
    app.add_handler(download_video_handler_callback)
    app.add_handler(back_to_previous_options_handler_callback)

