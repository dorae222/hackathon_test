FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	PYTHONPATH=/app

WORKDIR /app

# Install only what's needed and clean up in the same layer
RUN apt-get update \
	&& apt-get install -y --no-install-recommends bash libgl1 libglib2.0-0 \
	&& rm -rf /var/lib/apt/lists/*

# Dependencies first for better caching
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app/ ./app/

# Normalize line endings and permissions for entrypoint
RUN sed -i 's/\r$//' app/entrypoint.sh && chmod +x app/entrypoint.sh \
	&& mkdir -p /app/data /app/models /app/index \
	&& chown -R root:root /app

# Optional: Drop privileges (gunicorn can run as a non-root user)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["./app/entrypoint.sh"]
