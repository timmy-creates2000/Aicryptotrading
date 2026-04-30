#!/bin/bash
# Quick start script for Mac/Linux

echo
echo "===================================="
echo "  Crypto Trading Bot - Quick Start"
echo "===================================="
echo

# Check if venv exists
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

# Activate venv
echo "Activating virtual environment..."
source env/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo
    echo "WARNING: .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Edit .env and add your API keys:"
    echo "  - BYBIT_API_KEY"
    echo "  - BYBIT_API_SECRET"
    echo "  - GEMINI_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID"
    echo
    echo "Press Enter to continue..."
    read
fi

# Start bot
echo
echo "Starting crypto trading bot..."
echo

python main.py
