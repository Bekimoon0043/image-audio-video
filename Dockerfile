FROM python:3.10-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8000

# Use the PORT environment variable if provided (Render sets it)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
