# Use the official Python 3.11 slim image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8000 to allow communication to/from the container
EXPOSE 8000

# Command to run the application when the container starts
CMD ["python", "app.py"]
