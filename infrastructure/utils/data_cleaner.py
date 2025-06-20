import re
import string
from datetime import datetime
import unidecode
from typing import Optional

import utils.logging as logging_utils
from config import Config

config = Config()

class DataCleaner:
    @staticmethod
    def clean_text(text: Optional[str], words_to_remove: list = None) -> str:
        """Normaliza texto: remove pontuação, acentos, espaços extras e palavras específicas."""
        try:
            words_to_remove = words_to_remove or config.domain.words_to_remove

            if not text:
                return None
            text = unidecode.unidecode(text)
            text = text.translate(str.maketrans("", "", string.punctuation))
            text = text.upper().strip()
            text = re.sub(r"\s+", " ", text)

            if words_to_remove:
                pattern = r"\b(?:" + "|".join(map(re.escape, words_to_remove)) + r")\b"
                text = re.sub(pattern, "", text)
                text = re.sub(r"\s+", " ", text).strip()
        except Exception as e:
            # logging_utils.log_message(f"erro {e}", level="warning")
            pass

        return text

    @staticmethod
    def clean_number(text: str) -> float:
        """Converte número textual (BR/US) para float."""
        if not text:
            return None
        text = text.replace(".", "").replace(",", ".")
        try:
            return float(text)
        except Exception as e:
            # logging_utils.log_message(f"erro {e}", level="warning")
            return None

    @staticmethod
    def clean_date(text: Optional[str]) -> datetime:
        """Tenta converter string em datetime a partir de padrões comuns."""
        if not text:
            return None

        patterns = [
            "%d/%m/%Y %H:%M:%S",  # data + hora (BR)
            "%m/%d/%Y %H:%M:%S",  # US + hora
            "%Y-%m-%d %H:%M:%S",  # ISO + hora
            "%d/%m/%Y",           # data BR
            "%m/%d/%Y",           # data US
            "%Y-%m-%d",           # ISO
        ]
        for fmt in patterns:
            try:
                return datetime.strptime(text.strip(), fmt)
            except Exception as e:
                # logging_utils.log_message(f"erro {e}", level="warning")
                continue
        return None
