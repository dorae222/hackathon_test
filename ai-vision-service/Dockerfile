FROM python:3.11-slim

WORKDIR /app

# Install bash for entrypoint and clean up apt lists
RUN apt-get update \
	&& apt-get install -y --no-install-recommends bash \
	&& rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Ensure entrypoint has LF line endings in case of CRLF on Windows checkouts
RUN sed -i 's/\r$//' app/entrypoint.sh \
	&& chmod +x app/entrypoint.sh

# Create expected directories even if not copied at build-time
RUN mkdir -p /app/data /app/models /app/index

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["./app/entrypoint.sh"]
