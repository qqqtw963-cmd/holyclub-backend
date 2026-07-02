FROM python:3.9-slim-bookworm

RUN apt-get update && apt-get install -y gcc libcurl4-openssl-dev libssl-dev libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ARG CI=
ARG APP_ENV=prod
ENV APP_ENV=$APP_ENV
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN if [ -n "$CI" ]; then python manage.py cron --settings=config.settings.$APP_ENV; fi

CMD ["gunicorn", "--config", "gunicorn.conf.py"]
