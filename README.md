# Telegram Refuel Tracker Bot

A Telegram bot to track your vehicle's fuel consumption, costs, and efficiency. Keep detailed records of your refueling sessions with automatic calculations for price per liter and fuel efficiency.

## Features

- 📝 **Add Refuel Entries**: Track odometer readings, fuel amounts, and total prices
- 📊 **Automatic Calculations**: Price per liter and fuel efficiency (km/L) calculated automatically
- 📋 **Recent History**: View your last 10 refuel entries
- 📈 **Statistics**: Get comprehensive fuel consumption statistics
- 💾 **Local Storage**: Data stored in JSON format locally
- 🚗 **Distance Tracking**: Automatic calculation of distance between refuels

## Commands

- `/start` - Welcome message and introduction
- `/add` - Add a new refuel entry (interactive prompts)
- `/recent` - Show recent refuel entries (last 10)
- `/stats` - Display fuel consumption statistics
- `/help` - Show help information

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd telegram-refuel-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Telegram bot:**
   - Create a new bot with [@BotFather](https://t.me/botfather) on Telegram
   - Get your bot token
   - Copy `env.example` to `.env` and add your token:
     ```bash
     cp env.example .env
     ```
   - Edit `.env` and add your bot token:
     ```
     TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
     ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Usage

### Adding a Refuel Entry

1. Send `/add` to start the process
2. Enter your odometer reading in kilometers
3. Enter the fuel amount in liters
4. Enter the total price paid

The bot will automatically calculate:
- Price per liter
- Distance since last refuel (if applicable)
- Fuel efficiency (km/L)

### Example Session

```
User: /add
Bot: Let's add a new refuel entry!

Please send the odometer reading in kilometers:
User: 50000
Bot: Odometer: 50000 km

Now send the fuel amount in liters:
User: 45.5
Bot: Odometer: 50000 km
Liters: 45.5 L

Now send the total price:
User: 68.25
Bot: ✅ Refuel Added Successfully!

📅 Date: 2024-01-15 14:30
🛣️ Odometer: 50000 km
⛽ Fuel: 45.5 L
💰 Total Price: $68.25
💵 Price/Liter: $1.50
📏 Distance: 450 km
🚗 Efficiency: 9.89 km/L
```

## Data Storage

The bot stores all refuel data in `refuel_data.json` in the following format:

```json
[
  {
    "id": 1,
    "date": "2024-01-15T14:30:00.000000",
    "odometer": 50000,
    "liters": 45.5,
    "total_price": 68.25,
    "price_per_liter": 1.50,
    "distance_since_last": 450,
    "fuel_efficiency": 9.89
  }
]
```

## Statistics

The `/stats` command provides:
- Total number of refuels
- Total fuel consumed (liters)
- Total money spent
- Total distance traveled
- Average price per liter
- Average fuel efficiency

## Requirements

- Python 3.7+
- python-telegram-bot 20.7+
- python-dotenv 1.0.0+

## Security Notes

- Never commit your `.env` file with the actual bot token
- The `.gitignore` file is configured to exclude sensitive files
- Keep your bot token secure and don't share it publicly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
