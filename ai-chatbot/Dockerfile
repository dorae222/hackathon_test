FROM python:3.11-slim

# Faster, cleaner Python
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Leverage Docker layer caching for deps
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Drop privileges
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001
CMD ["gunicorn", "-c", "app/gunicorn_conf.py", "app.main:app"]
