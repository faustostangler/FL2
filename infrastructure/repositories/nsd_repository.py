"""SQLite-backed repository implementation for NSD data."""

from __future__ import annotations

from typing import List, Set, Tuple

from sqlalchemy.orm import Session

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, NSDRepositoryPort
from infrastructure.config import Config
from infrastructure.models.nsd_model import NSDModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyNsdRepository(SqlAlchemyRepositoryBase[NsdDTO, str], NSDRepositoryPort):
    """Concrete repository for NsdDTO using SQLite via SQLAlchemy."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger)

        self.config = config
        self.logger = logger

    def get_model_class(self) -> Tuple[type, tuple]:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return NSDModel, (NSDModel.nsd,)  # para PK simples

    def get_all_pending(
        self,
        company_names: Set[str],
        valid_types: Set[str],
        exclude_nsd: Set[str],
    ) -> List[NsdDTO]:
        """Retorna todos os NSDs que ainda não foram processados, filtrando por empresa, tipo e NSD.

        Args:
            company_names (Set[str]): Conjunto de nomes de empresas válidas.
            valid_types (Set[str]): Tipos de NSDs aceitos (ex: DFP, ITR...).
            exclude_nsd (Set[str]): Lista de códigos NSD já processados (raw ou parsed).

        Returns:
            List[NsdDTO]: Lista de NSDs pendentes.
        """
        with self.Session() as session:  # <=== aqui está a correção
            query = session.query(NSDModel).filter(
                NSDModel.company_name.in_(company_names),
                NSDModel.nsd_type.in_(valid_types),
                ~NSDModel.nsd.in_(exclude_nsd),
            )
            results = query.all()
        return sorted(
            [nsd.to_dto() for nsd in results],
            key=lambda dto: int(dto.nsd)
        )
