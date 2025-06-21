from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.config import Config
from infrastructure.logging import Logger

def create_data_cleaner(config: Config, logger: Logger) -> DataCleaner:
    """
    Fábrica parametrizada: recebe config e logger,
    devolve um DataCleaner pronto para uso.
    """
    return DataCleaner(config, logger)
