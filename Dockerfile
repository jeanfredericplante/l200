# Use the official Google Python lightweight base image
FROM python:3.12-slim

# Prevent python from writing pyc files to disk and enable instant logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establish working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for extremely fast package compilation
COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /bin/uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv into the system path
RUN uv pip install --system -r requirements.txt

# Copy backend and frontend codebase
COPY . .

# Expose port (Cloud Run sets PORT environment variable dynamically)
EXPOSE 8080

# Launch server
CMD ["python", "main.py"]
