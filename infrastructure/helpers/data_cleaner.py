import re
import string
import unidecode
from datetime import datetime
from typing import Optional, List

from infrastructure.config import Config
from infrastructure.logging import Logger

class DataCleaner:
    """
    Classe utilitária para normalização de dados brutos (textos, datas, números).
    Depende de configuração externa (ex: palavras a remover) e logger.
    """

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def clean_text(self, text: Optional[str], words_to_remove: Optional[List[str]] = None) -> Optional[str]:
        """Normaliza texto: remove pontuação, acentos, palavras específicas."""
        try:
            if not text:
                return None

            words_to_remove = words_to_remove or self.config.domain.words_to_remove

            text = unidecode.unidecode(text)
            text = text.translate(str.maketrans("", "", string.punctuation))
            text = text.upper().strip()
            text = re.sub(r"\s+", " ", text)

            if words_to_remove:
                pattern = r"\b(?:" + "|".join(map(re.escape, words_to_remove)) + r")\b"
                text = re.sub(pattern, "", text)
                text = re.sub(r"\s+", " ", text).strip()

            return text
        except Exception as e:
            self.logger.log(f"Erro ao limpar texto: {e}", level="warning")
            return None

    def clean_number(self, text: str) -> Optional[float]:
        """Converte número textual (BR/US) para float."""
        if not text:
            return None
        try:
            text = text.replace(".", "").replace(",", ".")
            return float(text)
        except Exception as e:
            self.logger.log(f"Erro ao limpar número: {e}", level="warning")
            return None

    def clean_date(self, text: Optional[str]) -> Optional[datetime]:
        """Tenta converter string em datetime a partir de padrões comuns."""
        if not text:
            return None

        patterns = [
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
        ]
        for fmt in patterns:
            try:
                return datetime.strptime(text.strip(), fmt)
            except Exception:
                continue

        self.logger.log(f"Erro ao limpar data: formato não reconhecido: '{text}'", level="debug")
        return None
