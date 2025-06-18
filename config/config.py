from pathlib import Path

class Config:
    def __init__(self):
        """ Initializes the configuration settings for the application.
        This includes setting up paths and other data.
        """
        # Folders and files
        TEMP_FOLDER = "temp"
        DATA_FOLDER = "data"
        LOG_FILE = "fly_logger.log"
        DB_NAME = "fly.db"

        # Database table names
        TBL_COMPANY_INFO = "tbl_company"

        # Paths
        root_path = Path(__file__).parent.parent.resolve()

        # Initialize paths
        self.paths = {
            "root_folder": root_path,
            "temp_folder": Path(TEMP_FOLDER),
            "data_folder": Path(DATA_FOLDER),
            "log_file": Path(TEMP_FOLDER) / LOG_FILE,
            "db_file": Path(DATA_FOLDER) / DB_NAME,
            # more paths...
        }

        # Create necessary directories
        for path in self.paths.values():
            path_obj = Path(path)
            folder = path_obj.parent if path_obj.suffix else path_obj
            folder.mkdir(parents=True, exist_ok=True)

        # Database configuration
        self.databases = {
            "default": {
                "name": DB_NAME,
                "filepath": Path(DATA_FOLDER) / DB_NAME,
                "tables": {
                    "company": TBL_COMPANY_INFO
                }
            }
        }

        # B3 API endpoints for different languages
        self.b3 = {
            "language": "pt-br",
            "endpoints": {
                "initial": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/",
                "detail": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetDetail/",
                "financial": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedFinancial/"
            }
        }

