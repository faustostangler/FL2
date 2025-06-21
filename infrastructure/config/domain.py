from dataclasses import dataclass, field

WORDS_TO_REMOVE = [
    "EM LIQUIDACAO",
    "EM LIQUIDACAO EXTRAJUDICIAL",
    "EXTRAJUDICIAL",
    "EM RECUPERACAO JUDICIAL",
    "EM REC JUDICIAL",
    "EMPRESA FALIDA"
]

@dataclass(frozen=True)
class DomainConfig:
    """Domain-specific configuration settings.

    Attributes:
        words_to_remove: List of words removed during text normalization.
        nsd_columns: Default NSD column names used when loading data.
    """

    # Configuration attributes with defaults from WORDS_TO_REMOVE
    words_to_remove: list = field(
        default_factory=lambda: WORDS_TO_REMOVE.copy()
    )

def load_domain_config() -> DomainConfig:
    """Load domain settings.

    Returns:
        DomainConfig: Instance with default ``words_to_remove`` and
        ``nsd_columns`` values.
    """

    # Load domain settings using default constants
    return DomainConfig(
        words_to_remove=WORDS_TO_REMOVE,
    )
