# infrastructure/repositories/nsd_repository.py

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from domain.dto.nsd_dto import NSDDTO

# from domain.ports.nsd_repository import NSDRepository
from infrastructure.config import Config
from infrastructure.logging import Logger
# from infrastructure.models import NSDModel  # Assumindo que foi movido de database.models


# class SQLiteNSDRepository(NSDRepository):
#     """
#     Implementação concreta do repositório NSD usando SQLite + SQLAlchemy.
#     Responsável por persistir objetos NSDDTO na tabela 'nsd_documents'.
#     """

#     def __init__(self, db_path: str = None):
#         self.db_path = db_path

#     def list_existing_ids(self) -> List[str]:
#         """
#         Retorna uma lista dos identificadores únicos dos documentos NSD
#         já salvos no banco (e.g., hash ou url).
#         """
#         with create_sqlite_session(self.db_path) as session:
#             result = session.execute(select(NSDModel.document_url)).scalars().all()
#             return result

#     def save_all(self, data: List[NSDDTO]) -> None:
#         """
#         Salva uma lista de documentos NSD no banco. Usa upsert simples
#         baseado em document_url como chave natural.
#         """
#         if not data:
#             return

#         with create_sqlite_session(self.db_path) as session:
#             for dto in data:
#                 existing = session.get(NSDModel, dto.document_url)
#                 if existing is None:
#                     model = NSDModel.from_dto(dto)
#                     session.add(model)
#             session.commit()

