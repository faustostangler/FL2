from dataclasses import dataclass, field

WORDS_TO_REMOVE = [
    "EM LIQUIDACAO",
    "EM LIQUIDACAO EXTRAJUDICIAL",
    "EXTRAJUDICIAL",
    "EM RECUPERACAO JUDICIAL",
    "EM REC JUDICIAL",
    "EMPRESA FALIDA",
]

# Default column names for NSD related data structures
NSD_COLUMNS = [
    "nsd",
    "company_name",
    "quarter",
    "version",
    "nsd_type",
    "dri",
    "auditor",
    "responsible_auditor",
    "protocol",
    "sent_date",
    "reason",
]

@dataclass(frozen=True)
class DomainConfig:
    """
    GlobalSettingsConfig holds global configuration settings for the application.

    Attributes:
        words_to_remove (list): A list of words to be removed, initialized with the default value from WORDS_TO_REMOVE.
        nsd_columns (list): Default column names for NSD data structures.
    """
    # Configuration attributes with defaults
    words_to_remove: list = field(default_factory=lambda: WORDS_TO_REMOVE.copy())
    nsd_columns: list = field(default_factory=lambda: NSD_COLUMNS.copy())

def load_domain_config() -> DomainConfig:
    """
    Loads the global domain configuration settings.

    Returns:
        GlobalSettingsConfig: An instance of GlobalSettingsConfig initialized with default constants for wait and save_threshold.
    """
    # Load domain settings using default constants
    return DomainConfig(
        words_to_remove=WORDS_TO_REMOVE,
        nsd_columns=NSD_COLUMNS,
    )
