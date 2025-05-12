# Weat API

A FastAPI-based backend service for managing places, tags, and more — built with Docker, OAuth2 authentication via AWS Cognito, and PostgreSQL.

## Getting Started

### Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Fill in any required values in `.env`.

### Running with Docker Compose

Build and start all services:

```bash
docker-compose up --build -d
```

Restart only the app service (if other services like DB are already running):

```bash
docker-compose up --build -d app
```

### Seed Database (Optional)

To import production data into your local Dockerized database:

```bash
docker exec -it weat-api-app ./scripts/seed_db.sh
```

### Testing

The project uses pytest for testing. To run all tests:
```bash
docker exec -it weat-api-app pytest
```

To run without integration tests:
```bash
docker exec -it weat-api-app pytest -m "not integration"
```

The tests are located in the `tests` directory and follow the same structure as the `app` directory. Each test file should be named `test_*.py` and test functions should be named `test_*`.

## License

MIT
