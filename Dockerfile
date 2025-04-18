FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

RUN mkdir -p /app/data

EXPOSE 8001
EXPOSE 8002
EXPOSE 3000

ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

CMD ["python", "main.py"]
