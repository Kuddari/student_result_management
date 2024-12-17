FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /employeesystem

# Upgrade pip and install supervisor
RUN pip install --upgrade pip && pip install supervisor

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run supervisord
CMD ["python","manage.py","runserver","0.0.0.0:8001"]