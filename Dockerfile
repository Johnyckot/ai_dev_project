# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Run migrations
RUN python manage.py migrate

# Expose the port
EXPOSE 8000

# Run the application with Daphne
CMD ["daphne", "quiz_app.asgi:application", "--bind", "0.0.0.0", "--port", "8000"]