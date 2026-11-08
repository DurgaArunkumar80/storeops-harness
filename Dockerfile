FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for FastAPI/Uvicorn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (excluding venv, git, etc. via .dockerignore)
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').getcode() == 200"

# Run the application
CMD ["uvicorn", "storeops.main:app", "--host", "0.0.0.0", "--port", "8000"]
