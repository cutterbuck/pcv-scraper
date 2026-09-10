FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY pcv ./pcv

# Unbuffered so logs appear in the App Platform runtime console immediately.
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "pcv"]
