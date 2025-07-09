# infrastructure/utils/id_generator.py
from __future__ import annotations

import hashlib
import time
import uuid
from typing import Optional

from infrastructure.config.config import Config


class IdGenerator:
    """
    Responsável por criar identificadores curtos, únicos e legíveis
    para threads ou processos de trabalho.

    • prefixo: nome da aplicação em maiúsculas (p.ex. “FLY”)
    • ts_part: timestamp em milissegundos, codificado em hexadecimal
    • rand_part: 8 hex pseudo-aleatórios do UUID-4
    """

    def __init__(self, config: Config, logger_name: str = "FLY") -> None:
        self.config = config
        self.logger_name = logger_name or self.config.global_settings.app_name or "FLY"

    def create_id(self, size: int = 0, string_id: Optional[str] = None) -> str:
        """Retorna um novo identificador no formato PREFIX-timestamp-random."""
        if string_id:
            full_id = string_id.encode("utf-8")
        else:
            rand_part = uuid.uuid4().hex
            ts_part = int(time.time() * 1000)
            salt_part = self.logger_name
            full_id = f"{salt_part}-{format(ts_part)}-{rand_part}".encode("utf-8")


        digest = hashlib.sha256(full_id).hexdigest()
        # digest = hashlib.sha512(full_id).hexdigest()


        return digest[:size] if size else digest
