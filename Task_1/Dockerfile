# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install any required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the main Python script when the container launches
# CMD ["python", "solution.py"]
