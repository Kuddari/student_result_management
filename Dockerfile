# Dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /kurusampanst

# Upgrade pip and install supervisor
RUN pip install --upgrade pip && pip install supervisor

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default command to run the service
CMD ["sh", "start.sh"]
