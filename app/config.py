import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    DEBUG = False

    SECRET_KEY = os.environ.get("SECRET_KEY")

    DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT", 5432)
    DATABASE_NAME = os.environ.get("DATABASE_NAME")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "weat-api-dev")


class TestingConfig(Config):
    DEBUG = True
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "weat-api-test")


class ProductionConfig(Config):
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "weat-api-prod")


def get_config_object():
    env = os.environ.get("ENVIRONMENT")

    if env == "dev":
        return DevelopmentConfig()
    elif env == "test":
        return TestingConfig()
    elif env == "prod":
        return ProductionConfig()
    else:
        raise Exception("ENVIRONMENT is not set")
