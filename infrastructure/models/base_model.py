from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# Historical alias used by tests
Base = BaseModel
