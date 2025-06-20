from config.paths import load_paths, PathConfig
from config.database import load_database_config, DatabaseConfig
from config.b3_api import load_b3_api_config, B3ApiConfig
from config.scraping import load_scraping_config, ScrapingConfig
from config.logging import load_logging_config, LoggingConfig
from config.global_settings import load_global_settings_config, GlobalSettingsConfig
from config.domain import load_domain_config, DomainConfig

class Config:
    """
    Aggregates all specialized configurations into a single object.
    Each attribute is an immutable and validated instance of its respective domain.
    """

    def __init__(self):
        """
        Initializes the configuration class by loading various configuration sections.

        Attributes:
            paths (PathConfig): Configuration for file and directory paths, loaded via `load_paths()`.
            database (DatabaseConfig): Database connection and settings, loaded via `load_database_config()`.
            b3 (B3ApiConfig): B3 API configuration, loaded via `load_b3_api_config()`.
            # scraping (ScrapingConfig): Scraping configuration, loaded via `load_scraping_config()` (currently commented out).

        Note:
            The scraping configuration is currently commented out and not loaded.
        """
        self.paths : PathConfig = load_paths()
        self.database : DatabaseConfig = load_database_config()
        self.b3 : B3ApiConfig = load_b3_api_config()
        self.scraping : ScrapingConfig = load_scraping_config()
        self.logging : LoggingConfig = load_logging_config()
        self.global_settings : GlobalSettingsConfig = load_global_settings_config()
        self.domain : DomainConfig = load_domain_config()
