# Use Python image as base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY main.py .

# Install any dependencies if needed
# RUN pip install ...

# Run the Python script when the container starts
CMD ["python", "main.py"]
