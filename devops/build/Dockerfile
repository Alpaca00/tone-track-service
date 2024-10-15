FROM python:3.12.2

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY ../.. /app

RUN /usr/local/bin/python -m pip install --upgrade pip \
 && pip install -r /app/requirements.txt

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=5 \
            CMD curl -f http://localhost:80/health || exit 1

RUN useradd -m appuser && chown -R appuser /app
USER appuser

WORKDIR /app
