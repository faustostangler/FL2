import re
import string
from datetime import datetime
from typing import List, Optional

import unidecode

from infrastructure.config import Config
from infrastructure.logging import Logger


class DataCleaner:
    """Utility class for normalizing raw text, dates and numbers.

    Requires external configuration (e.g. words to remove) and a logger.
    """

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def clean_text(
        self, text: Optional[str], words_to_remove: Optional[List[str]] = None
    ) -> Optional[str]:
        """Normalize a text string by removing punctuation, accents and stop words."""
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
            self.logger.log(f"Failed to clean text: {e}", level="warning")
            return None

    def clean_number(self, text: str) -> Optional[float]:
        """Convert a stringified number (BR/US formats) to ``float``."""
        if not text:
            return None
        try:
            text = text.replace(".", "").replace(",", ".")
            return float(text)
        except Exception as e:
            self.logger.log(f"Failed to clean number: {e}", level="warning")
            return None

    def clean_date(self, text: Optional[str]) -> Optional[datetime]:
        """Attempt to parse a date string using several common formats."""
        if isinstance(text, datetime):
            return text

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

        self.logger.log(
            f"Failed to parse date: unsupported format '{text}'",
            level="debug",
        )
        return None

    def clean_company_entry(self, entry: dict) -> dict:
        """Normalize relevant fields in a raw company listing entry."""

        text_keys = [
            "companyName",
            "issuingCompany",
            "tradingName",
            "segment",
            "segmentEng",
            "market",
        ]
        date_keys = ["dateListing"]

        for key in text_keys:
            if key in entry:
                entry[key] = self.clean_text(entry.get(key))

        for key in date_keys:
            if key in entry:
                entry[key] = self.clean_date(entry.get(key))

        return entry
