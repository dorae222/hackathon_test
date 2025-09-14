FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY data/ ./data/
ENV PYTHONPATH=/app
EXPOSE 8000
RUN chmod +x app/entrypoint.sh
CMD ["./app/entrypoint.sh"]
