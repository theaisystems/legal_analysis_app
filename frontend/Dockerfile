
# Use Python as the base image for running the backend
FROM python:3.10-slim AS backend


# Set environment variables for Microsoft SQL Server ODBC installation
ENV ACCEPT_EULA=Y

# Update the package repository and install required packages
RUN apt-get update && apt-get install -y curl unixodbc unixodbc-dev gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    apt-get install -y msodbcsql17 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# # Install system dependencies
# RUN apt-get update && \
#     apt-get install -y unixodbc unixodbc-dev && \
#     rm -rf /var/lib/apt/lists/*

# # Upgrade pip
# RUN pip install --upgrade pip

# Set the working directory for the backend
WORKDIR /app/backend

# Copy backend package files
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend application code
COPY . .

# Expose port for backend
EXPOSE 80

# Start backend application using uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["python","main.py"]
