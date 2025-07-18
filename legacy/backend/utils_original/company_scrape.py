import os
import re
import shutil
import sqlite3
import time

from bs4 import BeautifulSoup
from cachetools import TTLCache, cached
from selenium.webdriver.common.keys import Keys

from utils_original import selenium_driver, settings, system


class CompanyDataScraper:
    # Configuração de cache
    cache = TTLCache(maxsize=3000, ttl=60 * 5)

    def __init__(self):
        """Initialize the scraper with settings and WebDriver."""
        self.driver, self.driver_wait = selenium_driver.initialize_driver()

    @cached(cache)
    def get_raw_code(self):
        try:
            select_page_xpath = '//*[@id="selectPage"]'
            pagination_xpath = '//*[@id="listing_pagination"]/pagination-template/ul'
            nav_bloc_xpath = '//*[@id="nav-bloco"]/div'
            next_page_xpath = '//*[@id="listing_pagination"]/pagination-template/ul/li[10]/a'

            system.test_internet()
            self.driver.get(settings.companies_url)
            system.choose(select_page_xpath, self.driver, self.driver_wait)

            text = system.text(pagination_xpath, self.driver_wait)
            pages = list(map(int, re.findall(r"\d+", text)))
            total_pages = max(pages) - 1

            raw_code = []
            start_time = time.time()

            for i, page in enumerate(range(0, total_pages + 1)):
                system.wait_forever(self.driver_wait, nav_bloc_xpath)
                inner_html = system.raw_text(nav_bloc_xpath, self.driver_wait)
                raw_code.append(inner_html)

                if i != total_pages:
                    system.click(next_page_xpath, self.driver_wait)

                extra_info = [f"page {page + 1}"]
                system.print_info(i, total_pages + 1, start_time, extra_info)

        except Exception as e:
            system.log_error(e)
            raw_code = []

        return raw_code

    @cached(cache)
    def get_company_ticker(self):
        field_mapping = {
            "ticker": {"tag": "h5", "class": "card-title2"},
            "company_name": {"tag": "p", "class": "card-title"},
            "trading_name": {"tag": "p", "class": "card-text"},
            "listing": {"tag": "p", "class": "card-nome"},
        }

        raw_code = self.get_raw_code()
        company_tickers = {}

        for inner_html in raw_code:
            soup = BeautifulSoup(inner_html, "html.parser")
            cards = soup.find_all("div", class_="card-body")

            for card in cards:
                try:
                    extracted_info = {
                        key: system.clean_text(card.find(details["tag"], class_=details["class"]).text)
                        for key, details in field_mapping.items()
                    }

                    listing = extracted_info["listing"]
                    if listing:
                        for abbr, full_name in settings.governance_levels.items():
                            new_listing = system.clean_text(listing.replace(abbr, full_name))
                            if new_listing != listing:
                                extracted_info["listing"] = new_listing
                                break

                    company_tickers[extracted_info["company_name"]] = {
                        "ticker": extracted_info["ticker"],
                        "trading_name": extracted_info["trading_name"],
                        "listing": extracted_info["listing"],
                    }
                except Exception as e:
                    system.log_error(e)

        return company_tickers

    def extract_company_data(self, detail_soup):
        ticker_table_id = "accordionBody2"
        company_info = detail_soup.find("div", class_="card-body")

        ticker_codes = []
        isin_codes = []

        accordion_body = detail_soup.find("div", {"id": ticker_table_id})
        if accordion_body:
            rows = accordion_body.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    ticker_codes.append(system.clean_text(cols[0].text))
                    isin_codes.append(system.clean_text(cols[1].text))

        cnpj_element = company_info.find(text="CNPJ")
        cnpj = re.sub(r"\D", "", cnpj_element.find_next("p", class_="card-linha").text) if cnpj_element else ""
        activity_element = company_info.find(text="Atividade Principal")
        activity = activity_element.find_next("p", class_="card-linha").text if activity_element else ""
        sector_element = company_info.find(text="Classificação Setorial")
        sector_classification = sector_element.find_next("p", class_="card-linha").text if sector_element else ""
        website_element = company_info.find(text="Site")
        website = website_element.find_next("a").text if website_element else ""
        registrar_element = detail_soup.find(text="Escriturador")
        registrar = registrar_element.find_next("span").text.strip() if registrar_element else ""

        sectors = sector_classification.split("/")
        sector = system.clean_text(sectors[0].strip()) if len(sectors) > 0 else ""
        subsector = system.clean_text(sectors[1].strip()) if len(sectors) > 1 else ""
        segment = system.clean_text(sectors[2].strip()) if len(sectors) > 2 else ""

        return {
            "activity": activity,
            "sector": sector,
            "subsector": subsector,
            "segment": segment,
            "cnpj": cnpj,
            "website": website,
            "sector_classification": sector_classification,
            "ticker_codes": ticker_codes,
            "isin_codes": isin_codes,
            "registrar": registrar,
        }

    def get_company_info(self):
        existing_companies = self.load_existing_data()
        new_companies = self.get_company_ticker()

        all_company_info = {}

        companies_to_process = {name: info for name, info in new_companies.items() if name not in existing_companies}
        total_companies_to_process = len(companies_to_process)

        start_time = time.time()
        all_data = []

        for i, (company_name, info) in enumerate(companies_to_process.items()):
            try:
                system.test_internet()
                self.driver.get(settings.company_url)
                search_field_xpath = '//*[@id="keyword"]'
                nav_tab_content_xpath = '//*[@id="nav-tabContent"]'
                overview_xpath = '//*[@id="divContainerIframeB3"]/app-companies-overview/div/div[1]/div/div'

                search_field = system.wait_forever(self.driver_wait, search_field_xpath)
                search_field.clear()
                search_field.send_keys(company_name)
                search_field.send_keys(Keys.RETURN)

                system.wait_forever(self.driver_wait, nav_tab_content_xpath)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                cards = soup.find_all("div", class_="card-body")

                company_found = False
                for card in cards:
                    card_ticker = system.clean_text(card.find("h5", class_="card-title2").text)
                    if card_ticker == info["ticker"]:
                        card_xpath = f'//h5[text()="{card_ticker}"]'
                        system.click(card_xpath, self.driver_wait)
                        system.wait_forever(self.driver_wait, overview_xpath)

                        match = re.search(r"/main/(\d+)/", self.driver.current_url)
                        cvm_code = match.group(1) if match else ""
                        info["cvm_code"] = cvm_code

                        detail_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                        company_data = self.extract_company_data(detail_soup)

                        info.update(company_data)
                        company_found = True
                        break

            except Exception as e:
                system.log_error(f"Error processing company {company_name}: {e}")

            all_company_info[company_name] = info
            extra_info = [info["ticker"], info["cvm_code"], company_name]
            system.print_info(i, total_companies_to_process, start_time, extra_info)

            all_data.append({"company_name": company_name, **info})

            if (total_companies_to_process - i - 1) % (settings.batch_size // 1) == 0:
                all_data = self.save_to_db(all_data)
                all_data.clear()

        return existing_companies, companies_to_process

    def load_existing_data(self):
        existing_data = {}
        try:
            conn = sqlite3.connect(settings.db_filepath)
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {settings.company_table}")

            for row in cursor.fetchall():
                company_name = row[settings.company_columns.index("company_name")]
                existing_data[company_name] = dict(zip(settings.company_columns, row))

            conn.close()
        except Exception as e:
            system.log_error(e)

        return existing_data

    def save_to_db(self, data):
        try:
            os.makedirs(settings.data_folder, exist_ok=True)

            backup_name = f"{os.path.splitext(settings.db_filepath)[0]} {settings.backup_name}.db"
            backup_path = os.path.join(settings.data_folder, backup_name)
            if os.path.exists(settings.db_filepath):
                shutil.copyfile(settings.db_filepath, backup_path)

            conn = sqlite3.connect(settings.db_filepath)
            cursor = conn.cursor()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS company_info (
                                cvm_code TEXT,
                                company_name TEXT PRIMARY KEY,
                                ticker TEXT,
                                ticker_codes TEXT,
                                isin_codes TEXT,
                                trading_name TEXT,
                                sector TEXT,
                                subsector TEXT,
                                segment TEXT,
                                listing TEXT,
                                activity TEXT,
                                registrar TEXT,
                                cnpj TEXT,
                                website TEXT)"""
            )

            for info in data:
                cursor.execute(
                    """INSERT INTO company_info (cvm_code, company_name, ticker, ticker_codes, isin_codes, trading_name, sector, subsector, segment, listing, activity, registrar, cnpj, website)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(company_name) DO UPDATE SET
                                cvm_code=excluded.cvm_code,
                                ticker=excluded.ticker,
                                ticker_codes=excluded.ticker_codes,
                                isin_codes=excluded.isin_codes,
                                trading_name=excluded.trading_name,
                                sector=excluded.sector,
                                subsector=excluded.subsector,
                                segment=excluded.segment,
                                listing=excluded.listing,
                                activity=excluded.activity,
                                registrar=excluded.registrar,
                                cnpj=excluded.cnpj,
                                website=excluded.website""",
                    (
                        info["cvm_code"],
                        info["company_name"],
                        info["ticker"],
                        ",".join(info.get("ticker_codes", [])),
                        ",".join(info.get("isin_codes", [])),
                        info.get("trading_name", ""),
                        info.get("sector", ""),
                        info.get("subsector", ""),
                        info.get("segment", ""),
                        info.get("listing", ""),
                        info.get("activity", ""),
                        info.get("registrar", ""),
                        info.get("cnpj", ""),
                        info.get("website", ""),
                    ),
                )

            conn.commit()
            conn.close()

            print("Partial save completed...")
            return data

        except Exception as e:
            system.log_error(e)

    def update_and_save_batch(self, existing_data, new_data_batch):
        batch_to_save = []

        for info in new_data_batch:
            company_name = info["trading_name"]
            if company_name in existing_data:
                existing_info = existing_data[company_name]
                changes = {key: info[key] for key in info if info[key] != existing_info.get(key)}
                if changes:
                    batch_to_save.append(info)
            else:
                batch_to_save.append(info)

        self.save_to_db(batch_to_save)

    def main(self):
        existing_companies, new_companies = self.get_company_info()

        total_companies = len(new_companies)
        batch_size = settings.batch_size
        all_company_info = []

        for i in range(0, total_companies, batch_size):
            batch = list(new_companies.items())[i : i + batch_size]
            self.update_and_save_batch(existing_companies, [info for _, info in batch])
            all_company_info.extend(batch)

        system.db_optimize(settings.db_filepath)

        return all_company_info

    def close(self):
        """Fecha o WebDriver."""
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    try:
        scraper = CompanyDataScraper()
        scraper.run()
    except Exception as e:
        system.log_error(e)
    finally:
        scraper.close()
