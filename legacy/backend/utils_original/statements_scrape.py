import os
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
from threading import Lock

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils_original import selenium_driver, settings, system


class StatementsDataScraper:
    """A class to scrape and store statements data from NSD pages."""

    def __init__(self):
        """Initialize the scraper with settings and WebDriver."""
        self.driver, self.driver_wait = selenium_driver.initialize_driver()
        self.db_lock = Lock()
        pass

    def load_nsd_list(self):
        """Run NSD data from the nsd table in b3.db, filtered by
        settings.statements_types.

        Returns:
        DataFrame: A DataFrame containing the filtered NSD data.
        """
        try:
            query = """
                SELECT *
                FROM nsd
                WHERE nsd_type IN ({})
            """.format(",".join("?" for _ in settings.statements_types))

            with sqlite3.connect(settings.db_filepath) as conn:
                df = pd.read_sql_query(query, conn, params=settings.statements_types)

            df = df.drop_duplicates()

            return df
        except Exception as e:
            system.log_error(f"Error loading NSD data: {e}")
            return pd.DataFrame()

    def load_financial_statements(self):
        """Run existing financial statements from all .db files in the
        data_folder.

        Returns:
        dict: A dictionary where keys are sectors and values are DataFrames containing the NSD data for that sector.
        """
        try:
            specific_name = (
                f"{settings.db_name.split('.')[0]} {settings.statements_file}.{settings.db_name.split('.')[-1]}"
            )
            specific_db_path = os.path.join(settings.data_folder, specific_name)

            # Connect to the SQLite database
            conn = sqlite3.connect(specific_db_path)
            cursor = conn.cursor()

            # Query to get all table names, excluding internal SQLite tables like sqlite_stat1
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()

            total_files = len(tables)
            start_time = time.time()

            financial_statements = {}  # Initialize the dictionary to store sector DataFrames
            total_lines = 0
            for i, table in enumerate(tables):
                sector = table[0]
                df = pd.read_sql_query(f"SELECT * FROM {sector}", conn)

                if sector != "_":
                    sector = sector.upper().replace("_", " ")
                else:
                    pass
                financial_statements[sector] = df  # Store the DataFrame with the sector as the key

                # df.to_csv(f'{sector}.csv')

                # Display progress
                total_lines += len(df)
                extra_info = [f"{len(df)} lines in", sector, f"{total_lines} total lines"]
                system.print_info(i, total_files, start_time, extra_info)

                # print('break finantial statements loading')
                # break
            return financial_statements

        except Exception as e:
            system.log_error(f"Error loading existing NSD data: {e}")
            return {}

    def load_company_info(self):
        try:
            with sqlite3.connect(settings.db_filepath) as conn:
                query = "SELECT * FROM company_info"
                company_info_df = pd.read_sql_query(query, conn)
            return company_info_df
        except Exception as e:
            system.log_error(f"Error loading company_info data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error

    def scrape_financial_data(self, cmbGrupo, cmbQuadro):
        """Scrapes statements data from the specified page.

        Parameters:
        - group_value: The group combo box value.
        - quadro_value: The frame combo box value.

        Returns:
        - DataFrame: A DataFrame containing the scraped data.
        """
        try:
            drop_items = "3.99"
            xpath_grupo = '//*[@id="cmbGrupo"]'
            xpath_quadro = '//*[@id="cmbQuadro"]'
            xpath_frame = '//*[@id="iFrameFormulariosFilho"]'

            # Select the correct options for cmbGrupo and cmbQuadro
            grupo = system.select(xpath_grupo, cmbGrupo, self.driver, self.driver_wait)
            quadro = system.select(xpath_quadro, cmbQuadro, self.driver, self.driver_wait)

            # selenium enter frame
            frame = system.wait_forever(self.driver_wait, xpath_frame)
            frame = self.driver.find_elements(By.XPATH, xpath_frame)
            self.driver.switch_to.frame(frame[0])

            # read and clean quadro
            xpath = '//*[@id="ctl00_cphPopUp_tbDados"]'
            thousand = system.wait_forever(self.driver_wait, xpath)

            xpath = '//*[@id="TituloTabelaSemBorda"]'
            thousand = self.driver_wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text
            thousand = 1000 if "Mil" in thousand else 1

            html_content = self.driver.page_source
            df1 = pd.read_html(StringIO(html_content), header=0)[0]
            df2 = pd.read_html(StringIO(html_content), header=0, thousands=".")[0].fillna(0)

            df1 = df1.iloc[:, 0:3]
            df2 = df2.iloc[:, 0:3]
            df1.columns = settings.financial_statements_columns
            df2.columns = settings.financial_statements_columns
            df = pd.concat([df1.iloc[:, :2], df2.iloc[:, 2:3]], axis=1)

            col = df.iloc[:, 2].astype(str)
            col = col.str.replace(".", "", regex=False)
            col = col.str.replace(",", ".", regex=False)
            col = pd.to_numeric(col, errors="coerce")
            col = col * thousand
            df.iloc[:, 2] = col

            try:
                df = df[~df[settings.financial_statements_columns[0]].str.startswith(drop_items)]
            except Exception:
                pass

            # selenium exit frame
            self.driver.switch_to.parent_frame()

            return df

        except Exception:
            # system.log_error(e)
            return None

    def scrape_statements_data(self, cmbGrupo, cmbQuadro):
        """Process the scraped statements data into a DataFrame.

        Parameters:
        - cmbGrupo: The group combo box value.
        - cmbQuadro: The frame combo box value.

        Returns:
        DataFrame: A Pandas DataFrame containing the processed data.
        """
        try:
            # Define the XPaths
            xpath_grupo = '//*[@id="cmbGrupo"]'
            xpath_quadro = '//*[@id="cmbQuadro"]'
            xpath_frame = '//*[@id="iFrameFormulariosFilho"]'
            xpath_thousand = '//*[@id="UltimaTabela"]/table/tbody[1]/tr[1]/td[1]/b'
            thousand_word = "Mil"

            # XPaths for the different data points
            acoes_on_xpath = '//*[@id="QtdAordCapiItgz_1"]'
            acoes_pn_xpath = '//*[@id="QtdAprfCapiItgz_1"]'
            acoes_on_tesouraria_xpath = '//*[@id="QtdAordTeso_1"]'
            acoes_pn_tesouraria_xpath = '//*[@id="QtdAprfTeso_1"]'

            # Select the correct options for cmbGrupo and cmbQuadro
            grupo = system.select(xpath_grupo, cmbGrupo, self.driver, self.driver_wait)
            quadro = system.select(xpath_quadro, cmbQuadro, self.driver, self.driver_wait)

            # Selenium enter frame
            frame = system.wait_forever(self.driver_wait, xpath_frame)
            self.driver.switch_to.frame(frame)

            # Check if the values are in thousands
            thousand_text = system.wait_forever(self.driver_wait, xpath_thousand).text
            thousand = 1000 if thousand_word in thousand_text else 1

            # Extract the required values
            data = {
                settings.financial_statements_columns[0]: [],  # 'account'
                settings.financial_statements_columns[1]: [],  # 'description'
                settings.financial_statements_columns[2]: [],  # 'value'
            }

            # Extract values using the XPaths
            acoes_on = (
                self.driver.find_element(By.XPATH, acoes_on_xpath).text.strip().replace(".", "").replace(",", ".")
            )
            acoes_pn = (
                self.driver.find_element(By.XPATH, acoes_pn_xpath).text.strip().replace(".", "").replace(",", ".")
            )
            acoes_on_tesouraria = (
                self.driver.find_element(By.XPATH, acoes_on_tesouraria_xpath)
                .text.strip()
                .replace(".", "")
                .replace(",", ".")
            )
            acoes_pn_tesouraria = (
                self.driver.find_element(By.XPATH, acoes_pn_tesouraria_xpath)
                .text.strip()
                .replace(".", "")
                .replace(",", ".")
            )

            # Populate the data dictionary using settings values
            data[settings.financial_statements_columns[0]] = [
                settings.accounts["acoes_on"],
                settings.accounts["acoes_pn"],
                settings.accounts["acoes_on_tesouraria"],
                settings.accounts["acoes_pn_tesouraria"],
            ]
            data[settings.financial_statements_columns[1]] = [
                settings.descriptions["acoes_on"],
                settings.descriptions["acoes_pn"],
                settings.descriptions["acoes_on_tesouraria"],
                settings.descriptions["acoes_pn_tesouraria"],
            ]
            data[settings.financial_statements_columns[2]] = [
                float(acoes_on) * thousand,
                float(acoes_pn) * thousand,
                float(acoes_on_tesouraria) * thousand,
                float(acoes_pn_tesouraria) * thousand,
            ]

            df = pd.DataFrame(data)

            # Selenium exit frame
            self.driver.switch_to.parent_frame()

            return df

        except Exception:
            # system.log_error(f"Error processing statements data: {e}")
            return None

    def save_to_db(self, df, setor):
        """Save the processed statements data to a sector-specific table in the
        main database.

        Parameters:
        - df (DataFrame): The processed statements data as a DataFrame.
        - setor (str): The sector associated with the data.
        """

        try:
            # Construct the full path for the main database and its backup
            specific_name = (
                f"{settings.db_name.split('.')[0]} {settings.statements_file}.{settings.db_name.split('.')[-1]}"
            )
            specific_db_path = os.path.join(settings.data_folder, specific_name)

            backup_name = f"{settings.db_name.split('.')[0]} {settings.statements_file} {settings.backup_name}.{settings.db_name.split('.')[-1]}"
            backup_db_path = os.path.join(settings.data_folder, backup_name)

            # Create a sector table name with underscores instead of spaces
            table_name = setor.strip().replace(" ", "_") if setor.strip() else "_"

            # SQL command to create the table with a composite primary key
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                nsd INTEGER,
                sector TEXT,
                subsector TEXT,
                segment TEXT,
                company_name TEXT,
                quarter TEXT,
                version TEXT,
                type TEXT,
                frame TEXT,
                account TEXT,
                description TEXT,
                value REAL,
                PRIMARY KEY (company_name, quarter, version, type, frame, account, description)
            )
            """

            # SQL command for INSERT OR REPLACE
            insert_sql = f"""
            INSERT INTO {table_name} 
            (nsd, sector, subsector, segment, company_name, quarter, version, type, frame, account, description, value) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_name, quarter, version, type, frame, account, description) DO UPDATE SET
            nsd=excluded.nsd,
            sector=excluded.sector,
            subsector=excluded.subsector,
            segment=excluded.segment,
            type=excluded.type,
            frame=excluded.frame,
            account=excluded.account,
            description=excluded.description,
            value=excluded.value
            """

            # Acquire the lock before performing database operations
            with self.db_lock:
                print("skip backup file")
                # # Create a backup if the database already exists
                # if os.path.exists(specific_db_path):
                #     shutil.copyfile(specific_db_path, backup_db_path)
                # Connect to the main database
                with sqlite3.connect(specific_db_path) as conn:
                    # Enable WAL mode
                    conn.execute("PRAGMA journal_mode=WAL;")

                    # Create the table with the composite primary key if it doesn't exist
                    conn.execute(create_table_sql)
                    conn.commit()

                    # Insert data using INSERT OR REPLACE
                    for _, row in df.iterrows():
                        conn.execute(insert_sql, tuple(row))

                    conn.commit()

            print("Partial save completed...")
            return df

        except Exception as e:
            system.log_error(f"Error saving data for sector {setor}: {e}")

    def identify_targets(self):
        """Identifies and returns companies that need new financial data
        scraping.

        This function loads the NSD list, financial statements, and company information,
        filters out NSD entries already present in financial statements, and merges
        the remaining NSD entries with company information to identify the scrape targets.

        Returns:
            pd.DataFrame: A DataFrame containing the companies that need new financial data scraping.
        """
        last_order = "ZZZZZZZZZZ"
        scrape_order = ["sector", "subsector", "segment", "company_name", "quarter", "version"]

        try:
            # Run the necessary datasets
            nsd_list = self.load_nsd_list()
            company_info = self.load_company_info()

            # merge nsd and company info
            nsd_company_info = pd.merge(nsd_list, company_info, on="company_name", how="inner")

            # Group the merged DataFrame by sector and store in a dictionary
            nsd_list_by_sector = {
                sector if sector.strip() else "_": df for sector, df in nsd_company_info.groupby("sector")
            }

            financial_statements = self.load_financial_statements()

            scrape_target = []

            # Loop through each sector and filter out NSD entries that are already in financial statements
            for sector, df_nsd in nsd_list_by_sector.items():
                if sector in financial_statements:
                    # Filter out NSD entries that are already in the financial statements for the sector
                    filtered_df = df_nsd[~df_nsd["nsd"].isin(financial_statements[sector]["nsd"])]
                else:
                    # Include all NSD entries for sectors not in financial statements
                    filtered_df = df_nsd

                if not filtered_df.empty:
                    scrape_target.append(filtered_df)

            try:
                targets = pd.concat(scrape_target)
            except Exception:
                targets = pd.DataFrame(columns=settings.statements_columns)

            # Custom sorting to place empty fields last
            targets["sector"] = targets["sector"].replace("", last_order)  # Replace empty strings with a placeholder
            targets["subsector"] = targets["subsector"].replace("", last_order)
            targets["segment"] = targets["segment"].replace("", last_order)

            # Order the list by sector, subsector, segment, company_name, quarter, and version
            targets = targets.sort_values(by=scrape_order, ascending=True)

            # Restore empty fields
            targets["sector"] = targets["sector"].replace(last_order, "")  # Restore empty fields
            targets["subsector"] = targets["subsector"].replace(last_order, "")
            targets["segment"] = targets["segment"].replace(last_order, "")

            print(f"{len(nsd_list)} items found and {len(targets)} items to download")
            return targets

        except Exception as e:
            # Log any errors encountered during the process
            system.log_error(f"Error identifying scrape targets: {e}")

    def process_company_quarter_data(self, row):
        """Process financial and statements data for a specific company and
        quarter.

        Args:
            row (pd.Series): A row of data containing NSD, company name, quarter, sector, and other metadata.

        Returns:
            list: A list of DataFrames with the processed financial and statements data for the company.
        """
        try:
            company_quarter_data = []  # List to store data for the company in the current quarter

            # Extract data from the row
            nsd = row["nsd"]
            company_name = row["company_name"]
            quarter = pd.to_datetime(row["quarter"], dayfirst=False, errors="coerce").strftime("%Y-%m-%d")
            sector = row["sector"]
            subsector = row["subsector"]
            segment = row["segment"]
            version = row["version"]

            # Construct the URL for the NSD entry
            url = f"https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?NumeroSequencialDocumento={nsd}&CodigoTipoInstituicao=1"
            system.test_internet()
            self.driver.get(url)

            # Define all statements to be scraped
            statements = settings.financial_data_statements + settings.statements_data_statements

            for cmbGrupo, cmbQuadro in statements:
                # Determine which scraping method to use
                if [cmbGrupo, cmbQuadro] in settings.financial_data_statements:
                    df = self.scrape_financial_data(cmbGrupo, cmbQuadro)
                else:
                    df = self.scrape_statements_data(cmbGrupo, cmbQuadro)

                if df is not None:
                    # Add necessary metadata columns to the DataFrame
                    df = df.assign(
                        nsd=nsd,
                        company_name=company_name,
                        quarter=quarter,
                        version=version,
                        segment=segment,
                        subsector=subsector,
                        sector=sector,
                        type=cmbGrupo,
                        frame=cmbQuadro,
                    )
                    # Append the processed DataFrame to the list
                    company_quarter_data.append(df[settings.statements_columns])

            return company_quarter_data

        except Exception as e:
            # Log any errors encountered during processing
            system.log_error(f"Error processing company quarter data: {e}")
            return []  # Return an empty list to prevent the process from stopping

    def run_scraper(self, targets, batch_number=None):
        """Start the entire scraping process for the identified NSD entries,
        iterating over all financial data statements."""
        try:
            # Initialize the overall counter
            start_time = time.time()  # Record the start time for the entire process
            total_items = len(targets)  # Total number of items across all sectors

            # Initialize a counter to track the total number of processed items
            processed_items = 0
            targets_groups = targets.groupby("sector", sort=False)
            # Process data sector by sector, processing sectors with empty strings last
            for sector, sector_data in targets_groups:
                all_data = []  # List to store all the processed data

                for i, row in sector_data.iterrows():
                    try:
                        # Print progress information
                        extra_info = [
                            batch_number,
                            row["nsd"],
                            row["company_name"],
                            pd.to_datetime(row["quarter"], dayfirst=False, errors="coerce").strftime("%Y-%m-%d"),
                        ]
                        system.print_info(processed_items, total_items, start_time, extra_info)

                        # Process each company-quarter data using the refactored function
                        company_quarter_data = self.process_company_quarter_data(row)
                        all_data.extend(company_quarter_data)  # Add all processed DataFrames to all_data
                        number_to_save = (
                            settings.batch_size
                        )  # number_to_save = int(settings.batch_size // settings.max_workers)
                        # Save to DB every settings.batch_size iterations or at the end
                        if (total_items - processed_items - 1) % number_to_save == 0:
                            if all_data:
                                batch_df = pd.concat(all_data, ignore_index=True)
                                # Reorder columns and sort
                                batch_df = batch_df[settings.statements_columns].sort_values(
                                    by=settings.statements_order
                                )
                                db_filepath = self.save_to_db(batch_df, sector)
                                all_data.clear()  # Clear the list after saving
                                # Optimize the database after saving
                                # system.db_optimize(db_filepath)

                    except Exception as e:
                        # Log any errors encountered during processing of individual rows
                        system.log_error(f"Error processing row {i} in sector {sector}: {e}")

                    processed_items += 1  # Increment the processed items counter after each row

                # Optimize database after processing each sector
                if all_data:  # Make sure there is data to save
                    batch_df = pd.concat(all_data, ignore_index=True)
                    batch_df = batch_df[settings.statements_columns].sort_values(by=settings.statements_order)
                    db_filepath = self.save_to_db(batch_df, sector)
                    # system.db_optimize(db_filepath)

            return targets

        except Exception as e:
            # Log any errors encountered during the main scraping process
            system.log_error(f"Error in run_scraper: {e}")
            return None  # Return None to indicate that the scraping process did not complete

    def main_thread(self, targets, total_items, batch_size):
        try:
            with ThreadPoolExecutor(max_workers=settings.max_workers) as worker_pool_executor:
                futures = []
                for batch_index, start in enumerate(range(0, total_items, batch_size)):
                    end = min(start + batch_size, total_items)
                    futures.append(
                        worker_pool_executor.submit(
                            lambda targets=targets[start:end], index=batch_index + 0: (
                                self.run_scraper_with_new_instance(targets, index)
                            )
                        )
                    )

                for future in as_completed(futures):
                    future.result()  # This will raise an exception if one occurred in the thread

        except Exception as e:
            system.log_error(f"Error during batch processing: {e}")
        finally:
            self.close_scraper()

    def main_sequential(self, targets):
        """Sequentially process all scrape targets at once.

        Parameters:
        - targets (DataFrame): DataFrame containing all the targets to scrape.
        """
        try:
            # Process all scrape targets at once without batching
            self.run_scraper_with_new_instance(targets, batch_number=None)

        except Exception as e:
            system.log_error(f"Error during sequential processing: {e}")
        finally:
            self.close_scraper()

    def main(self, thread=True):
        self.close_scraper()

        # Identify the scrape targets
        targets = self.identify_targets()
        total_items = len(targets)
        batch_size = int(total_items / settings.max_workers)

        if batch_size == 0:
            thread = False

        if not targets.empty:
            if thread:
                # Start with threading
                self.main_thread(targets, total_items, batch_size)
            else:
                # Start sequentially
                self.main_sequential(targets)  # Pass only targets

        return True

    def run_scraper_with_new_instance(self, targets, batch_number):
        """Create a new instance of StatementsDataScraper and run the scraper.

        This ensures each batch has its own WebDriver instance.
        """
        scraper = StatementsDataScraper()
        try:
            scraper.run_scraper(targets, batch_number)
        finally:
            scraper.close_scraper()

    def close_scraper(self):
        """Close the WebDriver."""
        try:
            self.driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        scraper = StatementsDataScraper()
        scraper.run_scraper(group_value="Statements", quadro_value="Quadro Demonstrativo")
    except Exception as e:
        system.log_error(e)
    finally:
        scraper.close_scraper()
