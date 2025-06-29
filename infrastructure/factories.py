from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.config import Config
from infrastructure.logging import Logger


def create_data_cleaner(config: Config, logger: Logger) -> DataCleaner:
    """Factory that builds a ready-to-use ``DataCleaner`` instance."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("factories.create_data_cleaner() WHERE IS THIS?")
    return DataCleaner(config, logger)
