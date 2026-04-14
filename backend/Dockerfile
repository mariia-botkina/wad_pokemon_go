# Dockerfile – Minimal production image for the FastAPI backend.
#
# Build:  docker build -t pokemon-go-backend .
# Run:    docker run -p 8000:8000 pokemon-go-backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Expose the Uvicorn port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
