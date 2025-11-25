from telegram.ext import Application
from .start_handler import start_handler
from .error_handler import error_handler

def setup_handlers(app: Application):
    # Start handler
    app.add_handler(start_handler)

    # Error handler
    app.add_error_handler(error_handler)