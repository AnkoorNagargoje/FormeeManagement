# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies for wkhtmltopdf and Python packages
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    gcc \
    libpq-dev \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || (cat requirements.txt && exit 1)

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT Formee.wsgi:application

