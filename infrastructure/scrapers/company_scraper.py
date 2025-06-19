from typing import List, Dict, Optional, Set, Callable

import json
import base64
import requests
import time

import utils.logging as logging_utils
from config.config import Config
from infrastructure.scrapers.fetch_utils import _fetch_with_retry
from utils.data_cleaner import DataCleaner

config = Config()

class CompanyScraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """
    def __init__(self):
        """
        Initializes the SQLite database connection and ensures table creation.
        """
        logging_utils.log_message("Start CompanyScraper", level="info")

        self.language = config.b3["language"]
        self.endpoint_initial = config.b3["endpoints"]["initial"]
        self.endpoint_detail = config.b3["endpoints"]["detail"]
        self.endpoint_financial = config.b3["endpoints"]["financial"]

        self.session = requests.Session()

    def fetch_all(self, skip_cvm_codes: Optional[Set[str]] = None, save_callback: Optional[Callable[[List[dict]], None]] = None, save_threshold: Optional[int] = None) -> List[Dict]:
        """
        Fetches raw data for all companies.

        :return: List of dictionaries representing raw company data
        """
        logging_utils.log_message("Get Existing Companies", level="info")

        skip_cvm_codes = skip_cvm_codes or set()
        save_threshold = save_threshold or config.global_settings['save_threshold'] or 50

        buffer = []
        results = []
        initial = self._fetch_companies()

        logging_utils.log_message("Start CompanyScraper fetch_all", level="info")
        start_time = time.time()

        for i, entry in enumerate(initial):
            cvm_code = entry.get("codeCVM")
            if not cvm_code or cvm_code in skip_cvm_codes:
                continue

            try:
                detail = self._fetch_detail(str(cvm_code))
                parsed = self._parse_company(entry, detail)
                buffer.append(parsed)

                progress={"index": i, "size": len(initial), "start_time": start_time}
                logging_utils.log_message(f"cvm_code: {cvm_code} ", level="info", progress=progress)

                remaining_items = len(initial) - i - 1
                if (remaining_items % save_threshold == 0) or (remaining_items == 0):
                   if callable(save_callback):
                        save_callback(buffer)
                        logging_utils.log_message(f"Saved {len(buffer)} companies (partial)", level="info")
                        buffer.clear()

            except Exception as e:
                logging_utils.log_message(f"erro {e}", level="warning")

        return results

    def _fetch_companies(self) -> List[Dict]:
        """
        Busca o conjunto inicial de empresas disponíveis na B3.

        :return: Lista de empresas com código CVM e nome base.
        """
        PAGE_NUMBER = 1
        PAGE_SIZE = 120
        results = []
        start_time = time.time()

        while True:
            payload = {
                "language": self.language,
                "pageNumber": PAGE_NUMBER,
                "pageSize": PAGE_SIZE,
            }
            token = self._encode_payload(payload)
            url = self.endpoint_initial + token
            response = _fetch_with_retry(self.session, url)
            data = response.json()

            current_results = data.get("results", [])
            results.extend(current_results)

            total_pages = data.get("page", {}).get("totalPages", 1)

            progress = {
                "index": PAGE_NUMBER - 1,
                "size": total_pages,
                "start_time": start_time,
            }
            logging_utils.log_message(f"Page {PAGE_NUMBER}/{total_pages}", level="info", progress=progress)

            if PAGE_NUMBER >= total_pages:
                break

            PAGE_NUMBER += 1

        return results

    def _encode_payload(self, payload: dict) -> str:
        """
        Codifica um dicionário JSON para o formato base64 usado pela B3.

        :param payload: Dicionário de entrada
        :return: String base64
        """
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def _fetch_detail(self, cvm_code: str) -> Dict:
        """
        Busca os detalhes de uma empresa a partir do código CVM.

        :param cvm_code: Código CVM da empresa
        :return: Dicionário com detalhes estendidos da empresa
        """
        payload = {
            "codeCVM": cvm_code,
            "language": self.language
        }
        token = self._encode_payload(payload)
        url = self.endpoint_detail + token
        response = _fetch_with_retry(self.session, url)
        return response.json()

    def _parse_company(self, base: Dict, detail: Dict) -> Optional[Dict]:
        """
        Combina os dados do resultado base com os detalhes e retorna um dicionário padronizado.

        :param base: Dados iniciais da empresa (GetInitialCompanies)
        :param detail: Detalhes adicionais da empresa (GetDetail)
        :return: Dicionário padronizado
        """
        try:
            codes = detail.get("otherCodes", []) or []
            ticker_codes = [c["code"] for c in codes if "code" in c]
            isin_codes = [c["isin"] for c in codes if "isin" in c]

            # Classificação setorial
            industry = detail.get("industryClassification", "")
            parts = [p.strip() for p in industry.split("/")]

            ticker = DataCleaner.clean_text(base.get("issuingCompany"))
            company_name = DataCleaner.clean_text(base.get("companyName"))
            cvm_code = DataCleaner.clean_text(base.get("codeCVM"))
            cnpj = DataCleaner.clean_text(detail.get("cnpj"))
            trading_name = DataCleaner.clean_text(detail.get("tradingName"))
            listing = DataCleaner.clean_text(detail.get("listingSegment"))
            registrar = DataCleaner.clean_text(detail.get("registrar"))
            website = detail.get("website")
            sector = DataCleaner.clean_text(parts[0]) if len(parts) > 0 else None
            subsector = DataCleaner.clean_text(parts[1]) if len(parts) > 1 else None
            segment = DataCleaner.clean_text(parts[2]) if len(parts) > 2 else None

            market_indicator = DataCleaner.clean_text(base.get("marketIndicator") or detail.get("marketIndicator"))
            type_bdr = DataCleaner.clean_text(base.get("typeBDR") or detail.get("typeBDR"))
            date_listing = DataCleaner.clean_date(base.get("dateListing"))
            status = DataCleaner.clean_text(base.get("status") or detail.get("status"))
            segment_b3 = DataCleaner.clean_text(base.get("segment"))
            segment_eng = DataCleaner.clean_text(base.get("segmentEng"))
            company_type = DataCleaner.clean_text(base.get("type"))
            market = DataCleaner.clean_text(base.get("market") or detail.get("market"))
            industry = detail.get("industryClassification")
            industry_eng = detail.get("industryClassificationEng")
            activity = detail.get("activity")
            institution_common = DataCleaner.clean_text(detail.get("institutionCommon"))
            institution_pref = DataCleaner.clean_text(detail.get("institutionPreferred"))
            last_date = DataCleaner.clean_date(detail.get("lastDate"))
            category = DataCleaner.clean_text(detail.get("describleCategoryBVMF"))
            quotation_date = DataCleaner.clean_date(detail.get("dateQuotation"))

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
            logging_utils.log_message(f"erro {e}", level="debug")
            return None
