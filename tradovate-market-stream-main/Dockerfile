# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the time zone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project code
COPY . .

# Run your script
CMD ["python", "main.py"]