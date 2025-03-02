#!/bin/bash

# Navigate to your project directory (adjust if needed)
cd "$(dirname "$0")" || exit

# Activate the virtual environment
source .venv/bin/activate

# Run your Python script
python app.py

# Optional: Deactivate the virtual environment when done
deactivate