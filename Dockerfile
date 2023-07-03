# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the container
COPY main.py .

# Set environment variables for Gotify URL and token
ENV GOTIFY_URL=""

# Set the command to run your Python script
CMD [ "python", "main.py" ]