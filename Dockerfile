# Use a base image with Python
FROM python:3.11-slim AS builder

# Set environment variables for ODBC
ENV ODBC_VERSION=2.3.7
ENV ACCEPT_EULA=Y

# Install necessary packages and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install pytorch
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# Create a new image with only the necessary runtime dependencies
FROM python:3.11-slim

# Copy the necessary files from the builder image
COPY --from=builder /app /app

# Set the working directory
WORKDIR /app

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]

