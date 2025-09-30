"""Basic bot handlers for common commands."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

# Initialize database service
db_service = DatabaseService()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    
    try:
        # Create or get user from database
        db_user = db_service.create_or_get_user(user)
        
        welcome_message = (
            f"🚗 Welcome to the Refuel Tracker Bot, {user.first_name}!\n\n"
            "I help you track your vehicle's fuel consumption and costs.\n\n"
            "Available commands:\n"
            "• /addcar - Add a new car to your account\n"
            "• /cars - View all your cars\n"
            "• /setdefault - Set your default car\n"
            "• /deletecar - Delete a car (with confirmation)\n"
            "• /add - Add a new refuel entry\n"
            "• /recent - View recent refuel entries\n"
            "• /stats - View fuel consumption statistics\n"
            "• /me - Show your account information\n"
            "• /help - Show detailed help information\n\n"
            f"✅ Your account has been set up! (User ID: {db_user.id})\n"
            "Let's start by adding your first car with /addcar! ⛽"
        )
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Start command used by user {user.id} ({user.username}) - DB User ID: {db_user.id}")
        
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await update.message.reply_text(
            "Welcome to the Refuel Tracker Bot! 🚗\n\n"
            "I'm having trouble setting up your account right now. Please try again later."
        )

async def me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user account information."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found in database. Please use /start to create your account."
            )
            return
        
        # Get user statistics
        stats = db_service.get_user_stats(user.id)
        
        info_message = (
            f"👤 Your Account Information\n\n"
            f"🆔 Database ID: {db_user.id}\n"
            f"📱 Telegram ID: {db_user.telegram_id}\n"
            f"👤 Name: {db_user.first_name} {db_user.last_name or ''}\n"
            f"🏷️ Username: @{db_user.username or 'Not set'}\n"
            f"🌐 Language: {db_user.language_code or 'Not set'}\n"
            f"✅ Status: {'Active' if db_user.is_active else 'Inactive'}\n"
            f"📅 Member since: {db_user.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"📊 Statistics:\n"
            f"🚗 Cars: {stats.get('car_count', 0)}\n"
            f"⛽ Refuel entries: {stats.get('refuel_count', 0)}"
        )
        
        await update.message.reply_text(info_message)
        logger.info(f"Me command used by user {user.id}")
        
    except Exception as e:
        logger.error(f"Error in me_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't retrieve your account information right now. Please try again later."
        )

async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message (fallback handler)."""
    user_message = update.message.text
    response = f"Hello! You said: {user_message}\n\nUse /help to see available commands."
    await update.message.reply_text(response)
    logger.debug(f"Echo handler used by user {update.effective_user.id}")