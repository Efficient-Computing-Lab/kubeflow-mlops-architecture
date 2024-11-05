# Use Python image as base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY main.py .
COPY kfp_client.py .

# Install any dependencies if needed
RUN pip3 install kfp==2.7.0 flask werkzeug

EXPOSE 5005

# Run the Python script when the container starts
CMD ["python", "main.py"]
