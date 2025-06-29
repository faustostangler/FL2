# settings/database.py
import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > config > database")
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from .paths import load_paths

DB_FILENAME="fly.db"
TABLES = {
    # logic key : SQLite physical name
    "company": "tbl_company",
    "nsd": "tbl_nsd",
    "statements": "tbl_statements",
}


@dataclass(frozen=True)
class DatabaseConfig:
    """
    Configuração do banco de dados SQLite.
    Attributes:
        data_dir: Diretório onde o arquivo de banco será armazenado.
        db_file_name: Nome do arquivo SQLite.
        db_path: Caminho completo para o arquivo de banco.
        connection_string: URI de conexão SQLAlchemy.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("database class DatabaseConfig")

    data_dir: Path
    db_filename: str = field(default=DB_FILENAME)
    tables: Mapping[str, str] = field(default_factory=lambda: TABLES)
    connection_string: str = field(init=False)
    
    def __post_init__(self):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("DatabaseConfig __post_init__")

        # Calcula dinamicamente a URI de conexão
        object.__setattr__(
            self,
            "connection_string",
            f"sqlite:///{self.data_dir / self.db_filename}"
        )

def load_database_config() -> DatabaseConfig:
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("database.load_database_config()")

    paths = load_paths()

    return DatabaseConfig(
        data_dir = paths.data_dir,
        db_filename = DB_FILENAME,
        tables = TABLES, 
    )
