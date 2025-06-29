import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > config > paths")
from pathlib import Path
from dataclasses import dataclass, field, fields

# Subpastas nomeadas (relativas ao root)
TEMP_DIR = "temp"
LOG_DIR = "logs"
DATA_DIR = "data"

@dataclass(frozen=True)
class PathConfig:
    """
    Configura os caminhos principais do sistema.
    Attributes:
        root_dir: Diretório raiz absoluto do projeto (calculado automaticamente).
        temp_dir: Subpasta para arquivos temporários.
        log_dir: Subpasta para arquivos de log.
        data_dir: Subpasta para bancos de dados.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("config.paths.PathConfig")
    temp_dir: Path = field(init=False)
    log_dir: Path = field(init=False)
    data_dir: Path = field(init=False)
    root_dir: Path = field(init=False)

    def __post_init__(self):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("config.paths.PathConfig.__post_init__")
        # Define o root_dir como o diretório do projeto
        root = Path(__file__).resolve().parent.parent.parent
        object.__setattr__(self, "root_dir", root)
        object.__setattr__(self, "temp_dir", root / TEMP_DIR)
        object.__setattr__(self, "log_dir", root / LOG_DIR)
        object.__setattr__(self, "data_dir", root / DATA_DIR)

        # Cria as pastas se ainda não existirem
        for fld in fields(self):
            p = getattr(self, fld.name)
            if isinstance(p, Path) and fld.name != "root_dir":
                p.mkdir(parents=True, exist_ok=True)

def load_paths() -> PathConfig:
    """
    Cria e retorna uma instância de PathConfig com os diretórios garantidos.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("config.paths.load_paths")

    return PathConfig()
