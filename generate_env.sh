#!/bin/bash

echo "Generating .env file with random values"

echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
echo "API_KEY=$(openssl rand -hex 32)" >> .env
echo "SPS=$(openssl rand -hex 32)" >> .env
echo "POSTGRES_USER=root" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "POSTGRES_DB=tts" >> .env
echo "POSTGRES_HOST=postgres" >> .env
echo "REDIS_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "TF_ENABLE_ONEDNN_OPTS=0" >> .env

cp /app/.env /app/.env
