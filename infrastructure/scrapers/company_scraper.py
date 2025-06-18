from typing import List, Dict

class CompanyScraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """

    def fetch_all(self) -> List[Dict]:
        """
        Simulates fetching raw data for all companies.

        :return: List of dictionaries representing raw company data
        """
        return [
            {
                "ticker": "PETR4",
                "company_name": "Petrobras",
                "cnpj": "33.000.167/0001-01",
                "cvm_code": "9512",
                "ticker_codes": "PETR4, PETR3",
                "isin_codes": "BRPETRACNPR6",
                "trading_name": "PETROBRAS",
                "sector": "Petróleo",
                "subsector": "Exploração",
                "segment": "Energia",
                "listing": "Novo Mercado",
                "activity": "Exploração e produção de petróleo",
                "registrar": "Bradesco",
                "website": "http://www.petrobras.com.br",
            },
            {
                "ticker": "VALE3",
                "company_name": "Vale S.A.",
                "cnpj": "33.592.510/0001-54",
                "cvm_code": "2458",
                "ticker_codes": "VALE3",
                "isin_codes": "BRVALEACNOR0",
                "trading_name": "VALE",
                "sector": "Mineração",
                "subsector": "Metais",
                "segment": "Commodities",
                "listing": "Novo Mercado",
                "activity": "Extração de minério",
                "registrar": "Itaú",
                "website": "http://www.vale.com",
            }
        ]
