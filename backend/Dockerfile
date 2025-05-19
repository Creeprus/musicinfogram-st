FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .


RUN pip install -r requirements.txt


RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu dos2unix \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /app/data /app/media /app/static /app/fonts

COPY . .

COPY entrypoint.sh /app

RUN dos2unix /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"] 