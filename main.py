#!/usr/bin/env python3
"""Main entry point for the Telegram Refuel Bot."""

import sys
import os

# Add src to Python path for config.settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the bot from the renamed file
from telegram_bot import main

if __name__ == '__main__':
    main()
