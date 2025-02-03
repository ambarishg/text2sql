# Use a base image with Python
FROM python:3.11-slim

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

# Install Microsoft ODBC Driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*
    
COPY . /app
WORKDIR /app
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
