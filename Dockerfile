FROM python:3.12-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory for SQLite database
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

ENV PYTHONUNBUFFERED=1

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

VOLUME ["/app/data"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-", "app:app"]