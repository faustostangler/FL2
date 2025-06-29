from infrastructure.config import Config
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.logging import Logger


def create_data_cleaner(config: Config, logger: Logger) -> DataCleaner:
    """Factory that builds a ready-to-use ``DataCleaner`` instance."""
    return DataCleaner(config, logger)
