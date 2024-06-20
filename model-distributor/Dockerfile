# Use Python image as base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY main.py .
COPY send_file.py .
COPY service.py .

# Install any dependencies if needed
RUN pip3 install requests flask werkzeug

# Expose port 4443
EXPOSE 4443

# Run the Python script when the container starts
CMD ["python", "service.py"]
