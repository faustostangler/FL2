


# from pathlib import Path

# class Config:
#     def __init__(self):
#         """ Initializes the configuration settings for the application.
#         This includes setting up paths and other data.
#         """
#         # Folders and files
#         TEMP_FOLDER = "temp"
#         DATA_FOLDER = "data"
#         LOG_FILE = "fly_logger.log"
#         DB_NAME = "fly.db"

#         # Database table names
#         TBL_COMPANY_INFO = "tbl_company"

#         # Paths
#         root_path = Path(__file__).parent.parent.resolve()

#         # Initialize paths
#         self.paths = {
#             "base_dir": root_path,
#             "temp_folder": Path(TEMP_FOLDER),
#             "data_folder": Path(DATA_FOLDER),
#             "log_file": Path(TEMP_FOLDER) / LOG_FILE,
#             "db_file": Path(DATA_FOLDER) / DB_NAME,
#             # more paths...
#         }

#         # Create necessary directories
#         for path in self.paths.values():
#             path_obj = Path(path)
#             folder = path_obj.parent if path_obj.suffix else path_obj
#             folder.mkdir(parents=True, exist_ok=True)

#         # Database configuration
#         self.databases = {
#             "main": {
#                 "name": DB_NAME,
#                 "filepath": Path(DATA_FOLDER) / DB_NAME,
#                 "tables": {
#                     "company": TBL_COMPANY_INFO
#                 }
#             }
#         }

#         # B3 endpoints for different languages
#         self.b3 = {
#             "language": "pt-br",
#             "endpoints": {
#                 "initial": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/",
#                 "detail": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetDetail/",
#                 "financial": "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedFinancial/"
#             }
#         }

#         # Headers for web scraping
#         self.scraping = {
#             "test_internet": "https://www.google.com", # URL to test internet connectivity
#             "timeout": 5, # seconds
#             "max_attempts": 5, # Maximum attempts for retries
#             "user_agents": [
#                 # Chrome (Windows, macOS, Linux, Android)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",              
#                 # Firefox (Windows, macOS, Linux, Android)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1; rv:115.0) Gecko/20100101 Firefox/115.0",
#                 "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B; rv:115.0) Gecko/115.0 Firefox/115.0",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970; rv:115.0) Gecko/115.0 Firefox/115.0",
#                 # Safari (macOS, iOS)
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
#                 "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
#                 "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
#                 "Mozilla/5.0 (iPod; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
#                 "Mozilla/5.0 (AppleTV; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
#                 # Microsoft Edge (Windows, macOS)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Edg/114.0.1823.82",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Edg/114.0.1823.82",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Edg/114.0.1823.82",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36 Edg/114.0.1823.82",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Edg/114.0.1823.82",
#                 # Brave (Windows, macOS, Linux)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Brave/1.57.57",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Brave/1.57.57",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Brave/1.57.57",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36 Brave/1.57.57",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Brave/1.57.57",                
#                 # Opera (Windows, macOS)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 OPR/99.0.4788.88",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 OPR/99.0.4788.88",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 OPR/99.0.4788.88",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36 OPR/99.0.4788.88",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 OPR/99.0.4788.88",
#                 # Samsung Internet (Android)
#                 "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/114.0.5735.199 Mobile Safari/537.36",
#                 "Mozilla/5.0 (Linux; Android 13; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/114.0.5735.199 Mobile Safari/537.36",
#                 "Mozilla/5.0 (Linux; Android 13; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/114.0.5735.199 Mobile Safari/537.36",
#                 # Vivaldi Browser (Desktop and Android)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Vivaldi/6.1.3035.111",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Vivaldi/6.1.3035.111",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Vivaldi/6.1.3035.111",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Vivaldi/6.1.3035.111",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Vivaldi/6.1.3035.111",
#                 # Yandex Browser (Russia and CIS)
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 YaBrowser/23.7.3.652 Safari/537.36",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 YaBrowser/23.7.3.652 Safari/537.36",
#                 "Mozilla/5.0 (Android 13; Mobile; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 YaBrowser/23.7.3.652 Mobile Safari/537.36",
#                 "Mozilla/5.0 (Android 13; Tablet; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 YaBrowser/23.7.3.652 Safari/537.36",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 YaBrowser/23.7.3.652 Safari/537.36",
#                 # Xbox and PlayStation Browsers
#                 "Mozilla/5.0 (Xbox; U; Windows NT 10.0; WOW64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Edge/44.18363.8131",
#                 "Mozilla/5.0 (PlayStation 5; AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (PlayStation 4; AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Nintendo Switch; AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#                 "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
#             ], 
#             "referers": [
#                 "https://www.google.com/",
#                 "https://www.bing.com/",
#                 "https://www.duckduckgo.com/",
#                 "https://www.facebook.com/",
#                 "https://twitter.com/",
#                 "https://www.reddit.com/",
#                 "https://www.youtube.com/",
#                 "https://www.linkedin.com/",
#                 "https://www.instagram.com/",
#                 "https://www.tiktok.com/",
#                 "https://www.wikipedia.org/",
#                 "https://www.amazon.com/",
#                 "https://www.ebay.com/",
#                 "https://www.alibaba.com/",
#                 "https://www.github.com/",
#                 "https://stackoverflow.com/",
#                 "https://www.quora.com/",
#                 "https://news.ycombinator.com/",
#                 "https://www.netflix.com/",
#                 "https://www.twitch.tv/",
#                 "https://www.spotify.com/",
#                 "https://www.medium.com/",
#                 "https://www.dropbox.com/",
#                 "https://www.paypal.com/",
#                 "https://www.apple.com/",
#                 "https://www.microsoft.com/",
#                 "https://www.adobe.com/",
#                 "https://www.salesforce.com/",
#                 "https://www.oracle.com/",
#                 "https://www.ibm.com/",
#                 "https://www.cnn.com/",
#                 "https://www.bbc.com/",
#                 "https://www.nytimes.com/",
#                 "https://www.theguardian.com/",
#                 "https://www.aljazeera.com/",
#                 "https://www.reuters.com/",
#                 "https://www.forbes.com/",
#                 "https://www.bloomberg.com/",
#                 "https://www.wsj.com/",
#                 "https://www.ft.com/",
#                 "https://www.economist.com/",
#                 "https://www.nationalgeographic.com/",
#                 "https://www.history.com/",
#                 "https://www.sciencedaily.com/",
#                 "https://www.nature.com/",
#                 "https://www.sciencemag.org/",
#                 "https://www.arstechnica.com/",
#                 "https://www.techcrunch.com/",
#                 "https://www.wired.com/",
#                 "https://www.engadget.com/",
#             ],
#             "languages": [
#                 "en-US;q=1.0",  # English (United States)
#                 "en-GB;q=0.9",  # English (United Kingdom)
#                 "es-ES;q=0.9",  # Spanish (Spain)
#                 "es-MX;q=0.8",  # Spanish (Mexico)
#                 "fr-FR;q=0.9",  # French (France)
#                 "de-DE;q=0.9",  # German (Germany)
#                 "it-IT;q=0.8",  # Italian (Italy)
#                 "pt-BR;q=0.9",  # Portuguese (Brazil)
#                 "pt-PT;q=0.8",  # Portuguese (Portugal)
#                 "ja-JP;q=0.8",  # Japanese
#                 "zh-CN;q=0.8",  # Chinese (Simplified)
#                 "zh-TW;q=0.7",  # Chinese (Traditional)
#                 "ko-KR;q=0.8",  # Korean
#                 "ru-RU;q=0.9",  # Russian
#                 "ar-SA;q=0.8",  # Arabic (Saudi Arabia)
#                 "hi-IN;q=0.8",  # Hindi (India)
#                 "tr-TR;q=0.8",  # Turkish
#                 "nl-NL;q=0.8",  # Dutch (Netherlands)
#                 "sv-SE;q=0.8",  # Swedish (Sweden)
#                 "pl-PL;q=0.8",  # Polish
#                 "da-DK;q=0.8",  # Danish (Denmark)
#                 "no-NO;q=0.8",  # Norwegian
#                 "cs-CZ;q=0.8",  # Czech (Czech Republic)
#                 "el-GR;q=0.8",  # Greek
#                 "th-TH;q=0.8",  # Thai
#                 "id-ID;q=0.8",  # Indonesian
#                 "vi-VN;q=0.8",  # Vietnamese
#                 "fi-FI;q=0.8",  # Finnish
#                 "hu-HU;q=0.8",  # Hungarian
#                 "ro-RO;q=0.8",  # Romanian
#                 "bg-BG;q=0.8",  # Bulgarian
#                 "hr-HR;q=0.8",  # Croatian
#                 "sk-SK;q=0.8",  # Slovak
#                 "lt-LT;q=0.8",  # Lithuanian
#                 "lv-LV;q=0.8",  # Latvian
#                 "sl-SI;q=0.8",  # Slovenian
#                 "et-EE;q=0.8",  # Estonian
#                 "is-IS;q=0.8",  # Icelandic
#                 "mt-MT;q=0.8",  # Maltese
#                 "gl-ES;q=0.8",  # Galician (Spain)
#                 "ca-ES;q=0.8",  # Catalan (Spain)
#                 "eu-ES;q=0.8",  # Basque (Spain)
#                 "bs-BA;q=0.8",  # Bosnian (Bosnia and Herzegovina)
#                 "sr-RS;q=0.8",  # Serbian (Serbia)
#                 "mk-MK;q=0.8",  # Macedonian (North Macedonia)
#                 "uk-UA;q=0.8",  # Ukrainian (Ukraine)
#                 "hy-AM;q=0.8",  # Armenian (Armenia)
#                 "az-AZ;q=0.8",  # Azerbaijani (Azerbaijan)
#                 "ka-GE;q=0.8",  # Georgian (Georgia)
#                 "kk-KZ;q=0.8",  # Kazakh (Kazakhstan)
#             ]
#         }

#         self.global_settings = {
#             "wait": 2,
#             "save_threshold": 50,
#         }

#         self.domain = {
#             "words_to_remove": [
#                 "EM LIQUIDACAO",
#                 "EM LIQUIDACAO EXTRAJUDICIAL",
#                 "EXTRAJUDICIAL",
#                 "EM RECUPERACAO JUDICIAL",
#                 "EM REC JUDICIAL",
#                 "EMPRESA FALIDA"
#             ]
#         }
