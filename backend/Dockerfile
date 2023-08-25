FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y make

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["make", "run"]