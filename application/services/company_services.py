from application.usecases.sync_companies import SyncCompaniesUseCase
from domain.models.company_dto import CompanyDTO
from infrastructure.repositories.base_repository import BaseRepository
from infrastructure.scrapers.company_scraper import CompanyScraper

class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """

    def __init__(self, repository: BaseRepository[CompanyDTO], scraper: CompanyScraper):
        self.sync_usecase = SyncCompaniesUseCase(repository, scraper)

    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        self.sync_usecase.execute()
