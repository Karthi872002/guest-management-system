FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /guestmanagement

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Pre-create empty database file and set appuser ownership on WORKDIR
RUN touch /guestmanagement/db.sqlite3 && \
    adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /guestmanagement

USER appuser

EXPOSE 8000

# Run Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "guestmanagement.wsgi:application"]