#!/bin/bash
# Quick start script for AI Image Organizer

# Ensure dependencies are installed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Run the FastAPI server
uvicorn backend.app.main:app --reload

