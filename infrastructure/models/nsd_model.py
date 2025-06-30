from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from domain.dto.nsd_dto import NSDDTO

from .base_model import BaseModel


class NSDModel(BaseModel):
    """ORM model for the tbl_nsd table."""

    __tablename__ = "tbl_nsd"

    nsd: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column()
    quarter: Mapped[Optional[str]] = mapped_column()
    version: Mapped[Optional[str]] = mapped_column()
    nsd_type: Mapped[Optional[str]] = mapped_column()
    dri: Mapped[Optional[str]] = mapped_column()
    auditor: Mapped[Optional[str]] = mapped_column()
    responsible_auditor: Mapped[Optional[str]] = mapped_column()
    protocol: Mapped[Optional[str]] = mapped_column()
    sent_date: Mapped[Optional[str]] = mapped_column()
    reason: Mapped[Optional[str]] = mapped_column()

    @staticmethod
    def from_dto(dto: NSDDTO) -> "NSDModel":
        """Converts a NSDDTO into an NSDModel for persistence."""
        return NSDModel(
            nsd=dto.nsd,
            company_name=dto.company_name,
            quarter=dto.quarter,
            version=dto.version,
            nsd_type=dto.nsd_type,
            dri=dto.dri,
            auditor=dto.auditor,
            responsible_auditor=dto.responsible_auditor,
            protocol=dto.protocol,
            sent_date=dto.sent_date,
            reason=dto.reason,
        )

    def to_dto(self) -> NSDDTO:
        """Converts this ORM model back into a NSDDTO."""
        return NSDDTO(
            nsd=self.nsd,
            company_name=self.company_name,
            quarter=self.quarter,
            version=self.version,
            nsd_type=self.nsd_type,
            dri=self.dri,
            auditor=self.auditor,
            responsible_auditor=self.responsible_auditor,
            protocol=self.protocol,
            sent_date=self.sent_date,
            reason=self.reason,
        )
