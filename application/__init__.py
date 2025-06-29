import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("application __init__")
from .mappers.company_mapper import CompanyMapper

__all__ = ["CompanyMapper"]
