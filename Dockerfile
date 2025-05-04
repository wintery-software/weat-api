FROM python:3.13-slim

# Update package lists and install dependencie
RUN apt-get update \
    && apt-get install -y curl lsb-release ca-certificates \
    && echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
       > /etc/apt/sources.list.d/pgdg.list \
    && curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
       -o /etc/apt/trusted.gpg.d/postgres.asc \
    && apt-get update \
    && apt-get install -y bash postgresql-client-17

# Set the working directory to /app
WORKDIR /app

# Copy only the pyproject.toml file first to leverage Docker layer caching
COPY pyproject.toml .

# Upgrade pip and install the Python project (using pyproject.toml)
RUN pip install --upgrade pip \
    && pip install .

# Copy the rest of the application source code into the image
COPY . .

# Set the default command to run when the container starts
CMD ["./docker-entrypoint.sh"]
