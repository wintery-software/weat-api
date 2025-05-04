from typing import Annotated

from pydantic_settings import BaseSettings, SettingsConfigDict


def str_to_list(value: str) -> list[str]:
    """Convert a comma-separated string to a list of strings.

    Args:
        value (str): The comma-separated string to convert.

    Returns:
        list[str]: A list of strings.

    """
    return [item.strip() for item in value.split(",")]


class Settings(BaseSettings):
    """Settings for the application.

    This class is used to load and manage application settings from environment variables.

    """

    db_username: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

    @property
    def db_url(self) -> str:
        """Get the database URL.

        Returns:
            str: The database URL.

        """
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    cors_allow_origins: Annotated[str | None, str_to_list] = "*"
    place_search_similarity_threshold: float | None = None

    aws_region: str
    aws_auth_domain: str
    aws_cognito_client_id: str
    aws_cognito_user_pool_id: str

    @property
    def aws_cognito_authorization_url(self) -> str:
        """Get the AWS Cognito authorization URL.

        Returns:
            str: The AWS Cognito authorization URL.

        """
        return f"https://{self.aws_auth_domain}/oauth2/authorize"

    @property
    def aws_cognito_token_url(self) -> str:
        """Get the AWS Cognito token URL.

        Returns:
            str: The AWS Cognito token URL.

        """
        return f"https://{self.aws_auth_domain}/oauth2/token"

    @property
    def aws_cognito_jwks_url(self) -> str:
        """Get the AWS Cognito JWKS URL.

        Returns:
            str: The AWS Cognito JWKS URL.

        """
        return (
            f"https://cognito-idp.{self.aws_region}.amazonaws.com/{self.aws_cognito_user_pool_id}/.well-known/jwks.json"
        )

    @property
    def aws_cognito_issuer(self) -> str:
        """Get the AWS Cognito issuer URL.

        Returns:
            str: The AWS Cognito issuer URL.

        """
        return f"https://cognito-idp.{self.aws_region}.amazonaws.com/{self.aws_cognito_user_pool_id}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
