"""Bot application class for better organization."""

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config.settings import settings
from .handlers import (
    start_handler,
    echo_handler,
    me_handler,
    add_car_handler,
    cars_handler,
    set_default_car_handler,
    delete_car_handler,
    delete_car_confirm_handler
)

logger = logging.getLogger(__name__)

class RefuelBot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot application."""
        self.app = None
        self._validate_config()
    
    def _validate_config(self):
        """Validate bot configuration."""
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")
        
        try:
            settings.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _setup_handlers(self):
        """Set up all bot handlers."""
        # Command handlers
        self.app.add_handler(CommandHandler("start", start_handler))
        self.app.add_handler(CommandHandler("me", me_handler))
        self.app.add_handler(CommandHandler("addcar", add_car_handler))
        self.app.add_handler(CommandHandler("cars", cars_handler))
        self.app.add_handler(CommandHandler("setdefault", set_default_car_handler))
        self.app.add_handler(CommandHandler("deletecar", delete_car_handler))
        self.app.add_handler(CommandHandler("deletecar_confirm", delete_car_confirm_handler))
        
        # Message handler (fallback for non-command messages)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
        
        logger.info("All handlers registered successfully")
    
    def create_app(self):
        """Create and configure the bot application."""
        self.app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        return self.app
    
    def run(self):
        """Run the bot."""
        if not self.app:
            self.create_app()
        
        logger.info("Bot starting (polling)...")
        self.app.run_polling()
