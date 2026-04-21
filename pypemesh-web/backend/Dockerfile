FROM python:3.12-slim

WORKDIR /app

# Install core package (bundled alongside backend)
COPY pypemesh-core /app/pypemesh-core
COPY pypemesh-web/backend /app/backend

WORKDIR /app/backend

RUN pip install --no-cache-dir /app/pypemesh-core && \
    pip install --no-cache-dir -e .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
