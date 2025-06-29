import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > config > scraping")
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

TEST_INTERNET = "https://www.google.com"  # URL usada para verificar conectividade
TIMEOUT = 1  # Tempo máximo de espera em cada requisição (em segundos)
MAX_ATTEMPTS = 5  # Número máximo de tentativas em caso de falha

USER_AGENTS_JSON = "user_agents.json"  # Arquivo JSON com User-Agents
REFERERS_JSON = "referers.json"  # Arquivo JSON com Referers
LANGUAGES_JSON = "languages.json"  # Arquivo JSON com Accept-Language

@dataclass(frozen=True)
class ScrapingConfig:
    """
    Configurações gerais para web-scraping.
    Attributes:
        test_internet: URL usada para verificar conectividade.
        timeout: Tempo máximo de espera em cada requisição.
        max_attempts: Número máximo de tentativas em caso de falha.
        user_agents: Lista de User-Agent, carregada de user_agents.json.
        referers: Lista de Referer, carregada de referers.json.
        languages: Lista de Accept-Language, carregada de languages.json.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("scraping class ScrapingConfig")

    user_agents: List[str]
    referers: List[str]
    languages: List[str]
    test_internet: str = field(default=TEST_INTERNET)
    timeout: int = field(default=TIMEOUT)
    max_attempts: int = field(default=MAX_ATTEMPTS)

def load_scraping_config() -> ScrapingConfig:
    """
    Cria e retorna uma instância de ScrapingConfig.
    Os valores de test_internet, timeout e max_attempts ficam aqui,
    enquanto user_agents, referers e languages vêm de arquivos JSON separados.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("scraping load_scraping_config")

    base = Path(__file__).parent

    user_agents = json.loads((base / USER_AGENTS_JSON).read_text(encoding="utf-8"))
    referers = json.loads((base / REFERERS_JSON).read_text(encoding="utf-8"))
    languages = json.loads((base / LANGUAGES_JSON).read_text(encoding="utf-8"))

    return ScrapingConfig(
        user_agents=user_agents,
        referers=referers,
        languages=languages, 
        test_internet=TEST_INTERNET,
        timeout=TIMEOUT,
        max_attempts=MAX_ATTEMPTS
    )
