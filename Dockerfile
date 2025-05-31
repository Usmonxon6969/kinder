FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev \
        dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Copy project
COPY . /app/

# Create a non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Make sure the script is executable by everyone
RUN chmod 755 /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Set entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

# Run the application
CMD ["uvicorn", "kindergarten_meal_system.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
