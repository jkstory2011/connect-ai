# Base image
FROM python:3.12-slim

# Install system deps for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements (placeholder)
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command (overridden by DockerOperator)
CMD ["python", "-c", "print('worker ready')"]