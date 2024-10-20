#!/bin/bash

echo "Generating .env file with random values"

echo "SECRET_KEY=$(openssl rand -base64 32)" > .envi
echo "API_KEY=$(openssl rand -hex 32)" >> .envi
echo "SPS=$(openssl rand -hex 32)" >> .envi
echo "POSTGRES_USER=root" >> .envi
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .envi
echo "POSTGRES_DB=tts" >> .envi
echo "POSTGRES_HOST=postgres" >> .envi
echo "REDIS_PASSWORD=$(openssl rand -hex 16)" >> .envi
echo "TF_ENABLE_ONEDNN_OPTS=0" >> .envi

cp /app/.envi /app/.envi
