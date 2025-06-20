from dataclasses import dataclass, field

WAIT = 2 # Default wait time in seconds
SAVE_THRESOLD = 50 # Default threshold for saving data


@dataclass(frozen=True)
class GlobalSettingsConfig:
    """
    GlobalSettingsConfig class holds global configuration settings.

    Attributes:
        wait (int): The waiting time, initialized with the value of WAIT.
        save_threshold (int): The threshold for saving, initialized with the value of SAVE_THRESOLD.

    Logic Steps:
    1. Define class attributes for configuration parameters. # Define attributes for wait and save_threshold
    2. Use 'field' to set default values from external constants (WAIT, SAVE_THRESOLD). # Set defaults using WAIT and SAVE_THRESOLD
    3. These settings can be used throughout the application for consistent configuration. # Use these settings app-wide
    """

    # Configuration attributes with defaults from WAIT and SAVE_THRESOLD
    wait: int = field(default=WAIT)
    save_threshold: int = field(default=SAVE_THRESOLD)

def load_global_settings_config() -> GlobalSettingsConfig:
    """
    Loads and returns a GlobalSettingsConfig instance with default global settings.

    Returns:
        GlobalSettingsConfig: An instance initialized with the default WAIT and SAVE_THRESOLD values.

    Logic Steps:
    1. Use the WAIT and SAVE_THRESOLD constants as configuration values.
    2. Create and return a GlobalSettingsConfig instance with these values.
    """
    # Load global settings using default constants
    return GlobalSettingsConfig(
        wait=WAIT,
        save_threshold=SAVE_THRESOLD,
    )
