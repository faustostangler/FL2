import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > config > logging")
from dataclasses import dataclass, field
from pathlib import Path
from .paths import load_paths

LOG_FILENAME = "fly_logger.log" # Nome do arquivo de log padrão
LEVEL = "INFO"  # Nível de log padrão

@dataclass(frozen=True)
class LoggingConfig:
    """
    Logging system configuration.
    Attributes:
        log_dir: Directory where logs will be saved.
        log_file_name: Name of the log file.
        level: Default logging level.
        full_path: Full path to the log file.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("logging class LoggingConfig")
    log_dir: Path
    log_file_name: str = field(default=LOG_FILENAME)
    level: str = field(default=LEVEL)

    @property
    def full_path(self) -> Path:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("LoggingConfig.full_path()")
        return self.log_dir / self.log_file_name

def load_logging_config() -> LoggingConfig:
    """
    Creates and returns an instance of LoggingConfig,
    ensuring that the log directory exists.

    Returns:
        LoggingConfig: The logging configuration object with directory, filename, and level.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("logging_config load_logging_config")
    # Load application paths using the load_paths function
    paths = load_paths()

    # Return a LoggingConfig instance with the loaded log directory, default filename, and level
    return LoggingConfig(
        log_dir=paths.log_dir,
        log_file_name=LOG_FILENAME,
        level=LEVEL,
    )
