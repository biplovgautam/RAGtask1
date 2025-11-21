# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which is not needed for production images
# --upgrade pip: Ensures we have the latest version of pip
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Command to run the application
# We bind to 0.0.0.0 to allow external connections.
# Render will automatically set the PORT environment variable and map it.
# We'll use port 10000 as a common default for web services.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
