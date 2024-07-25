#!/bin/bash

# Check if the bot is already running
if pgrep -f rpgta5rp_bot.py > /dev/null
then
    echo "Bot is already running."
    exit 1
else
    echo "Starting bot..."
    python3 /home/user/RoulettePrediction/rpgta5rp_bot.py
fi

