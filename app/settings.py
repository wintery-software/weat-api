from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application.

    This class is used to load and manage application settings from environment variables.

    """

    db_username: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

    cors_allow_origins: str = "*"  # optional, default to "*"
    place_search_similarity_threshold: float | None = None  # optional

    api_base_url: str | None = None  # optional

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_allow_origins_list(self) -> list[str]:
        """Get the list of allowed CORS origins.

        Returns:
            list[str]: A list of allowed CORS origins.

        """
        return self.cors_allow_origins.split(",") if self.cors_allow_origins else []


settings = Settings()
