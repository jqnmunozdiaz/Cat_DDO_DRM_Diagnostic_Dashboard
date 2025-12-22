# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# gcc and python3-dev might be needed for some python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any exact dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port to the outside world
EXPOSE 8080

# Run the application
# Using shell form to allow variable expansion for $PORT
CMD gunicorn --bind 0.0.0.0:$PORT app:server
