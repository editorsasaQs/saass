FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]