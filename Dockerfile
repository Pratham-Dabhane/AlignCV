# Optimized Dockerfile for AlignCV Production Deployment
FROM python:3.11-slim

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_LOGGER_LEVEL=error
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_optimized.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_optimized.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application with optimizations
CMD ["streamlit", "run", "frontend/app_v2.py", \
    "--server.fileWatcherType", "none", \
    "--server.enableCORS", "false", \
    "--server.enableXsrfProtection", "false", \
    "--browser.gatherUsageStats", "false", \
    "--logger.level", "error", \
    "--server.port", "8501", \
    "--server.address", "0.0.0.0"]
