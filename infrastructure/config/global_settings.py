from dataclasses import dataclass, field

WAIT = 2  # Default wait time in seconds
THRESOLD = 50  # Default threshold for saving data
MAX_LINEAR_HOLES = 2000  # Maximum number of linear holes allowed
MAX_WORKERS = 1  # Default number of threads for sync operations
BATCH_SIZE = 50  # Number of items per repository batch
QUEUE_SIZE = 100  # Max queue size for producer/consumer pipeline


@dataclass(frozen=True)
class GlobalSettingsConfig:
    """
    GlobalSettingsConfig class holds global configuration settings.

    Attributes:
        wait (int): The waiting time, initialized with the value of WAIT.
        threshold (int): The threshold for saving, initialized with the value of THRESOLD.

    Logic Steps:
    1. Define class attributes for configuration parameters. # Define attributes for wait and threshold
    2. Use 'field' to set default values from external constants (WAIT, THRESOLD). # Set defaults using WAIT and THRESOLD
    3. These settings can be used throughout the application for consistent configuration. # Use these settings app-wide
    """

    # Configuration attributes with defaults from WAIT and THRESOLD
    wait: int = field(default=WAIT)
    threshold: int = field(default=THRESOLD)
    max_linear_holes: int = field(default=MAX_LINEAR_HOLES)
    max_workers: int = field(default=MAX_WORKERS)
    batch_size: int = field(default=BATCH_SIZE)
    queue_size: int = field(default=QUEUE_SIZE)


def load_global_settings_config() -> GlobalSettingsConfig:
    """
    Loads and returns a GlobalSettingsConfig instance with default global settings.

    Returns:
        GlobalSettingsConfig: An instance initialized with the default WAIT and THRESOLD values.

    Logic Steps:
    1. Use the WAIT and THRESOLD constants as configuration values.
    2. Create and return a GlobalSettingsConfig instance with these values.
    """
    # Load global settings using default constants
    return GlobalSettingsConfig(
        wait=WAIT,
        threshold=THRESOLD,
        max_linear_holes=MAX_LINEAR_HOLES,
        max_workers=MAX_WORKERS,
        batch_size=BATCH_SIZE,
        queue_size=QUEUE_SIZE,
    )
