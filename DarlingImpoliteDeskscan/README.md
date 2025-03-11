
# Ilmli Uzbek Telegram Bot

A bilingual Telegram bot for the Ilmli Uzbek charity project, supporting both Russian and Uzbek languages.

## Features

- Bilingual support (Russian and Uzbek)
- Information about the charity project
- Donation information
- Contact details
- User language preferences stored in SQLite database

## Setup

1. Create a Telegram bot using [@BotFather](https://t.me/BotFather) and get your API token
2. Add your bot token to the `.env` file
3. Place an image named `about_us.jpg` in the root directory or the bot will create a default one
4. Run the bot: `python main.py`

## Commands

- `/start` - Start the bot (will use previously selected language if available)
- `/language` - Change language preference
