FROM python:3.12.2

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY ../.. /app

RUN /usr/local/bin/python -m pip install --upgrade pip \
 && pip install -r /app/requirements.txt

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 5000
CMD [""]
