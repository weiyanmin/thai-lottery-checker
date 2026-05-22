#!/bin/bash

# Start the Telegram bot in the background
python3 -m bot.main &

# Start the FastAPI server in the foreground
uvicorn api.server:app --host 0.0.0.0 --port $PORT
