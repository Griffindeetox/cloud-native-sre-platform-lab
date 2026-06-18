FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

ENV APP_VERSION=0.5.0
ENV OTEL_SERVICE_NAME=sre-fastapi-app

ENV ENVIRONMENT=container

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


