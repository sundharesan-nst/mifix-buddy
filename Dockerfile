# Use official Python image as base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (if needed, you can also use a .env file)
ENV PYTHONUNBUFFERED=1

# Expose the required port
EXPOSE 8000

# Entry point to run the application
CMD ["python", "app.py"]
