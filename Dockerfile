FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --upgrade pip \
 && pip install .

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
