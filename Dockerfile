FROM python:3.12-slim

# Security: jalankan sebagai non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements dulu (biar layer cache optimal)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ganti ownership ke appuser
RUN chown -R appuser:appuser /app

# Switch ke non-root user
USER appuser

CMD ["python", "bot_runner.py"]