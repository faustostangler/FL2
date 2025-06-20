from typing import List, Dict, Optional, Set, Callable

import json
import base64
import requests
import time

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.data_cleaner import DataCleaner

class CompanyB3Scraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """
    def __init__(self, config: Config, logger: Logger, data_cleaner: DataCleaner):
        """Set up configuration, logger and helper utilities for the scraper.

        Args:
            config (Config): Global configuration with B3 endpoints.
            logger (Logger): Logger used for progress and error messages.

        Attributes:
            config (Config): Stored configuration instance.
            logger (Logger): Stored logger instance.
            fetch_utils (FetchUtils): Utility for HTTP requests with retries.
            language (str): Language code for B3 API requests.
            endpoint_companies_list (str): URL for the companies list endpoint.
            endpoint_detail (str): URL for the company detail endpoint.
            endpoint_financial (str): URL for the financial data endpoint.
            session (requests.Session): Reusable HTTP session.

        Returns:
            None
        """
        # Store configuration and logger for use throughout the scraper
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner

        # Log the initialization of the CompanyB3Scraper
        self.logger.log("Start CompanyB3Scraper", level="info")

        # Initialize FetchUtils for HTTP request utilities
        self.fetch_utils = FetchUtils(config, logger)

        # Set language and API endpoints from configuration
        self.language = config.b3.language
        self.endpoint_companies_list = config.b3.endpoints["initial"]
        self.endpoint_detail = config.b3.endpoints["detail"]
        self.endpoint_financial = config.b3.endpoints["financial"]

        # Initialize a requests session for HTTP requests
        self.session = requests.Session()

    def fetch_all(self, skip_cvm_codes: Optional[Set[str]] = None, save_callback: Optional[Callable[[List[dict]], None]] = None, save_threshold: Optional[int] = None) -> List[Dict]:
        """
        Fetches raw data for all companies.

        :return: List of dictionaries representing raw company data
        """
        # Ensure skip_cvm_codes is a set (to avoid None and allow fast lookup)
        skip_cvm_codes = skip_cvm_codes or set()
        # Determine the save threshold (number of companies before saving buffer)
        save_threshold = save_threshold or self.config.global_settings.save_threshold or 50

        # Fetch the initial list of companies from B3, possibly skipping some CVM codes
        companies_list = self._fetch_companies_list(skip_cvm_codes, save_threshold)
        # Fetch and parse detailed information for each company, with optional skipping and periodic saving
        companies = self._fetch_companies_details(companies_list, skip_cvm_codes, save_callback, save_threshold)

        # Return the complete list of parsed company details
        return companies

    def _fetch_companies_list(self, skip_cvm_codes: Optional[Set[str]] = None, save_threshold: Optional[int] = None) -> List[Dict]:
        """
        Busca o conjunto inicial de empresas disponíveis na B3.

        :return: Lista de empresas com código CVM e nome base.
        """
        # Set initial pagination parameters
        PAGE_NUMBER = 1
        PAGE_SIZE = 120
        self.logger.log("Get Existing Companies", level="info")

        results = []
        start_time = time.time()

        # Loop through all pages of company data
        while True:
            # Build the payload for the current page
            payload = {
            "language": self.language,
            "pageNumber": PAGE_NUMBER,
            "pageSize": PAGE_SIZE,
            }
            # Encode the payload as required by the B3 API
            token = self._encode_payload(payload)
            url = self.endpoint_companies_list + token

            # Fetch the current page of results with retry logic
            response = self.fetch_utils.fetch_with_retry(self.session, url)
            data = response.json()

            # Extract and accumulate results from the current page
            current_results = data.get("results", [])
            results.extend(current_results)

            # Determine the total number of pages from the response
            total_pages = data.get("page", {}).get("totalPages", 1)

            # Log progress for monitoring
            progress = {
            "index": PAGE_NUMBER - 1,
            "size": total_pages,
            "start_time": start_time,
            }
            self.logger.log(f"Page {PAGE_NUMBER}/{total_pages}", level="info", progress=progress)

            # Check if all pages have been processed
            if PAGE_NUMBER >= total_pages:
                break

            # Move to the next page
            PAGE_NUMBER += 1

        # Return the complete list of companies
        return results

    def _encode_payload(self, payload: dict) -> str:
        """
        Codifica um dicionário JSON para o formato base64 usado pela B3.

        :param payload: Dicionário de entrada
        :return: String base64
        """
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def _fetch_companies_details(self, companies_list: List[Dict], skip_cvm_codes: Optional[Set[str]] = None, save_callback: Optional[Callable[[List[dict]], None]] = None, save_threshold: Optional[int] = None) -> List[Dict]:
        """
        Fetches and parses detailed information for a list of companies, with optional skipping and periodic saving.
        Args:
            companies_list (List[Dict]): List of company dictionaries, each containing at least a "codeCVM" key.
            skip_cvm_codes (Optional[Set[str]], optional): Set of CVM codes to skip during processing. Defaults to None.
            save_callback (Optional[Callable[[List[dict]], None]], optional): Callback function to save buffered company details periodically. Defaults to None.
            save_threshold (Optional[int], optional): Number of companies to process before triggering the save_callback. If not provided, uses configuration or defaults to 50.
        Returns:
            List[Dict]: List of parsed company detail dictionaries.
        Logs:
            - Progress and status information at each step.
            - Warnings for any exceptions encountered during processing.
        Raises:
            - Does not raise exceptions; logs warnings instead.
        """
        
        # Determine the save threshold (number of companies before saving buffer)
        save_threshold = save_threshold or self.config.global_settings.save_threshold or 50

        # Log the start of the fetch_all process for company details
        self.logger.log("Start CompanyB3Scraper fetch_all", level="info")

        # Initialize buffer for periodic saving and results for all parsed companies
        buffer = []
        results = []

        # Record the start time for progress logging
        start_time = time.time()

        # Iterate over each company entry in the list
        for i, entry in enumerate(companies_list):
            cvm_code = entry.get("codeCVM")
            # Skip if cvm_code is missing or in the skip list
            if not cvm_code or cvm_code in skip_cvm_codes:
                continue

            try:
                # Fetch detailed company data
                detail = self._fetch_detail(str(cvm_code))
                # Parse and standardize company data
                parsed = self._parse_company(entry, detail)
                buffer.append(parsed)
                results.append(parsed)

                # Log progress
                progress = {"index": i, "size": len(companies_list), "start_time": start_time}
                self.logger.log(f"cvm_code: {cvm_code} ", level="info", progress=progress)

                # Check if it's time to save the buffer
                remaining_items = len(companies_list) - i - 1
                if (remaining_items % save_threshold == 0) or (remaining_items == 0):
                    if callable(save_callback):
                        save_callback(buffer)
                        self.logger.log(f"Saved {len(buffer)} companies (partial)", level="info")
                        buffer.clear()

            except Exception as e:
                # Log any exception as a warning
                self.logger.log(f"erro {e}", level="warning")

        # Return the list of all parsed company details
        return results

    def _fetch_detail(self, cvm_code: str) -> Dict:
        """
        Busca os detalhes de uma empresa a partir do código CVM.

        :param cvm_code: Código CVM da empresa
        :return: Dicionário com detalhes estendidos da empresa
        """
        # Prepare the payload with the CVM code and language for the request
        payload = {
            "codeCVM": cvm_code,
            "language": self.language
        }
        # Encode the payload as base64 to match B3 API requirements
        token = self._encode_payload(payload)
        # Build the full URL for the detail endpoint
        url = self.endpoint_detail + token
        # Fetch the company detail data with retry logic
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        # Return the parsed JSON response
        return response.json()

    def _parse_company(self, base: Dict, detail: Dict) -> Optional[Dict]:
        """
        Combina os dados do resultado base com os detalhes e retorna um dicionário padronizado.

        :param base: Dados iniciais da empresa (Getcompanies_listCompanies)
        :param detail: Detalhes adicionais da empresa (GetDetail)
        :return: Dicionário padronizado
        """
        try:
            # Extract and clean company fields from base and detail data
            codes = detail.get("otherCodes", []) or []
            ticker_codes = [c["code"] for c in codes if "code" in c]
            isin_codes = [c["isin"] for c in codes if "isin" in c]

            # Classificação setorial
            industry = detail.get("industryClassification", "")
            parts = [p.strip() for p in industry.split("/")]

            ticker = self.data_cleaner.clean_text(base.get("issuingCompany"))
            company_name = self.data_cleaner.clean_text(base.get("companyName"))
            cvm_code = self.data_cleaner.clean_text(base.get("codeCVM"))
            cnpj = self.data_cleaner.clean_text(detail.get("cnpj"))
            trading_name = self.data_cleaner.clean_text(detail.get("tradingName"))
            listing = self.data_cleaner.clean_text(detail.get("listingSegment"))
            registrar = self.data_cleaner.clean_text(detail.get("registrar"))
            website = detail.get("website")
            sector = self.data_cleaner.clean_text(parts[0]) if len(parts) > 0 else None
            subsector = self.data_cleaner.clean_text(parts[1]) if len(parts) > 1 else None
            segment = self.data_cleaner.clean_text(parts[2]) if len(parts) > 2 else None

            market_indicator = self.data_cleaner.clean_text(base.get("marketIndicator") or detail.get("marketIndicator"))
            type_bdr = self.data_cleaner.clean_text(base.get("typeBDR") or detail.get("typeBDR"))
            date_listing = self.data_cleaner.clean_date(base.get("dateListing"))
            status = self.data_cleaner.clean_text(base.get("status") or detail.get("status"))
            segment_b3 = self.data_cleaner.clean_text(base.get("segment"))
            segment_eng = self.data_cleaner.clean_text(base.get("segmentEng"))
            company_type = self.data_cleaner.clean_text(base.get("type"))
            market = self.data_cleaner.clean_text(base.get("market") or detail.get("market"))
            industry = detail.get("industryClassification")
            industry_eng = detail.get("industryClassificationEng")
            activity = detail.get("activity")
            institution_common = self.data_cleaner.clean_text(detail.get("institutionCommon"))
            institution_pref = self.data_cleaner.clean_text(detail.get("institutionPreferred"))
            last_date = self.data_cleaner.clean_date(detail.get("lastDate"))
            category = self.data_cleaner.clean_text(detail.get("describleCategoryBVMF"))
            quotation_date = self.data_cleaner.clean_date(detail.get("dateQuotation"))

            return {
                "ticker": ticker,
                "company_name": company_name,
                "cvm_code": cvm_code,
                "cnpj": cnpj,
                "trading_name": trading_name,
                "listing": listing,
                "registrar": registrar,
                "website": website,
                "ticker_codes": json.dumps(ticker_codes),
                "isin_codes": json.dumps(isin_codes),
                "otherCodes": codes,
                "sector": sector,
                "subsector": subsector,
                "segment": segment,

                "marketIndicator": market_indicator,
                "typeBDR": type_bdr,
                "dateListing": date_listing,
                "status": status,
                "segment_b3": segment_b3,
                "segmentEng": segment_eng,
                "type": company_type,
                "market": market,
                "industryClassification": industry,
                "industryClassificationEng": industry_eng,
                "activity": activity,
                "hasQuotation": detail.get("hasQuotation"),
                "institutionCommon": institution_common,
                "institutionPreferred": institution_pref,
                "lastDate": last_date,
                "hasEmissions": detail.get("hasEmissions"),
                "hasBDR": detail.get("hasBDR"),
                "describleCategoryBVMF": category,
                "dateQuotation": quotation_date,
            }
        except Exception as e:
            self.logger.log(f"erro {e}", level="debug")
            return None
