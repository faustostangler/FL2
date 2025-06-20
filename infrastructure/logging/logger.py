import logging
from typing import Optional
from infrastructure.config.config import Config
from infrastructure.logging.progress_formatter import ProgressFormatter
from infrastructure.logging.context_tracker import ContextTracker


class Logger:
    """
    Logger da aplicação FLY.
    Encapsula configuração, contexto e formatação de progresso.
    Usa o sistema de logging nativo do Python.
    """

    def __init__(self, config: Config, level: str = "DEBUG"):
        self.config = config
        self.logger = self._setup_logger(level)
        self.progress_formatter = ProgressFormatter()
        self.context_tracker = ContextTracker(config.paths.root_dir)

    def _setup_logger(self, level: str) -> logging.Logger:
        """
        Configura o logger nativo do Python com handlers para terminal e arquivo.
        """
        log_path = self.config.logging.full_path
        logger = logging.getLogger("FLY")
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # Console
            sh = logging.StreamHandler()
            sh.setLevel(getattr(logging, level.upper(), logging.INFO))
            sh.setFormatter(formatter)
            logger.addHandler(sh)

            # Arquivo
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger
    def log(self, message: str, level: str = "info", progress: Optional[dict] = None):
        """
        Registra uma mensagem com contexto e progresso, se aplicável.
        """
        context_msg = self.context_tracker.get_context() if level.lower() == "debug" else ""
        progress_msg = self.progress_formatter.format(progress) if progress else ""

        full_message = message
        if context_msg:
            full_message += f" | {context_msg}"
        if progress_msg:
            full_message += f" | {progress_msg}"

        try:
            log_fn = getattr(self.logger, level.lower(), self.logger.info)
            log_fn(full_message)
        except Exception as e:
            print(f"Logging failed: {e}")
            print(f"Logging failed: {e}")



# from pathlib import Path
# import logging
# import inspect
# import time
# from infrastructure.config.config import Config


# class Logger:
#     """
#     Central logger for the FLY application.
#     Encapsulates logging logic for terminal and file with support for progress and context.
#     """

#     # Holds the singleton instance of the logger
#     _logger_instance = None

#     def __init__(self, config: Config):
#         self.config = config
#         self.project_root = config.paths.root_dir
#         self.logger = self._get_logger()

#     def _get_logger(self, name=None, level: str = "DEBUG") -> logging.Logger:
#         """
#         Cria e retorna uma instância singleton de logger com handlers de terminal e arquivo.
#         """
#         numeric_level = getattr(logging, level.upper(), logging.DEBUG)

#         if Logger._logger_instance is not None:
#             Logger._logger_instance.setLevel(numeric_level)
#             for handler in Logger._logger_instance.handlers:
#                 handler.setLevel(numeric_level)
#             return Logger._logger_instance

#         log_path = self.config.logging.full_path
#         name = name or Path(log_path).stem

#         logger = logging.getLogger(name)
#         logger.setLevel(logging.DEBUG)

#         formatter = logging.Formatter(
#             "%(asctime)s %(levelname)s: %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S"
#         )

#         stream_handler = logging.StreamHandler()
#         stream_handler.setLevel(numeric_level)
#         stream_handler.setFormatter(formatter)
#         logger.addHandler(stream_handler)

#         file_handler = logging.FileHandler(log_path)
#         file_handler.setLevel(numeric_level)
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)

#         Logger._logger_instance = logger
#         return logger

#     def _format_progress(self, progress: dict) -> str:
#         """
#         Gera uma string com progresso, tempo decorrido, tempo restante e tempo total estimado.
#         """
#         if not progress:
#             return ""

#         try:
#             index = progress.get("index", 0)
#             size = progress.get("size", 1)
#             start = progress.get("start_time", time.time())
#             now = time.time()

#             completed = index + 1
#             percent = completed / size
#             elapsed = now - start
#             avg = elapsed / completed
#             remaining = (size - completed) * avg
#             total_est = elapsed + remaining

#             def fmt(seconds):
#                 h, rem = divmod(int(seconds), 3600)
#                 m, s = divmod(rem, 60)
#                 return f"{h}h{m:02}m{s:02}s"

#             return f"{completed}/{size} | {percent:.4%} | {fmt(elapsed)} + {fmt(remaining)} = {fmt(total_est)}"
#         except Exception:
#             return ""

#     def _get_context(self) -> str:
#         """
#         Extrai o contexto de chamada dentro do projeto com base na stack trace.
#         """
#         try:
#             stack = inspect.stack()
#             relevant = []

#             for frame in stack:
#                 path = Path(frame.filename).resolve()
#                 if self.project_root in path.parents:
#                     rel_path = path.relative_to(self.project_root)
#                     relevant.append(f"line {frame.lineno} of {frame.function}() in '{rel_path}'")

#             return " <- ".join(relevant[3:-1])
#         except Exception:
#             return ""

#     def log(self, message, name=None, level: str = "debug", progress=None):
#         """
#         Registra uma mensagem no logger configurado com informações de progresso e stack trace.
#         """
#         logger = self._get_logger(name, level=level)
#         progress_msg = self._format_progress(progress) if progress else ""
#         context = self._get_context()

#         full_message = f"{message} | {context}" if level.lower() == "debug" else message
#         if progress_msg:
#             full_message += f" | {progress_msg}"

#         try:
#             log_fn = getattr(logger, level.lower(), logger.info)
#             log_fn(full_message)
#         except Exception as e:
#             print(f"Logging failed: {e}")

# # =============================================================================================================

# from pathlib import Path
# import logging
# import inspect
# import time

# _logger_instance = None
# config = Config()

# def _get_logger(name=None, level:str="DEBUG") -> logging.Logger:
#     """
#     Cria e retorna uma instância singleton de logger com handlers de terminal e arquivo.

#     Args:
#         name (str, optional): Nome do logger. Se não for fornecido, usa o nome do arquivo de log.
#         level (str): Nível de log mínimo. Ex: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".

#     Returns:
#         logging.Logger: Instância configurada do logger.
#     """
#     # Converte string para constante numérica do módulo logging
#     numeric_level = getattr(logging, level.upper(), logging.DEBUG)

#     global _logger_instance
#     if _logger_instance is not None:
#         _logger_instance.setLevel(numeric_level)
#         for handler in _logger_instance.handlers:  # type: ignore #
#             handler.setLevel(numeric_level)
#         return _logger_instance

#     log_path = config.logging.full_path
#     name = name or Path(log_path).stem  # Usa o nome do arquivo como fallback

#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)

#     # Define o formato do log
#     formatter = logging.Formatter(
#         "%(asctime)s %(levelname)s: %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S"
#     )

#     # Saída para o terminal
#     stream_handler = logging.StreamHandler()
#     stream_handler.setLevel(numeric_level)
#     stream_handler.setFormatter(formatter)
#     logger.addHandler(stream_handler)

#     # Saída para arquivo
#     file_handler = logging.FileHandler(log_path)
#     file_handler.setLevel(numeric_level)
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)

#     _logger_instance = logger
#     return logger

# def _format_progress(progress: dict) -> str:
#     """
#     Gera uma string com progresso, tempo decorrido, tempo restante e tempo total estimado.

#     Args:
#         progress (dict): Dicionário com chaves:
#             - index (int): Índice atual do item.
#             - size (int): Tamanho total da sequência.
#             - start_time (float): Timestamp inicial (time.time()).

#     Returns:
#         str: String formatada com informações de progresso. Exemplo: "15/100 | 15.0% | 0h00m10s + 0h01m00s = 0h01m10s"
#     """
#     if not progress:
#         return ""

#     try:
#         index = progress.get("index", 0)
#         size = progress.get("size", 1)
#         start = progress.get("start_time", time.time())
#         now = time.time()

#         completed = index + 1
#         percent = completed / size
#         elapsed = now - start
#         avg = elapsed / completed
#         remaining = (size - completed) * avg
#         total_est = elapsed + remaining

#         def fmt(seconds):
#             h, rem = divmod(int(seconds), 3600)
#             m, s = divmod(rem, 60)
#             return f"{h}h{m:02}m{s:02}s"

#         return f"{completed}/{size} | {percent:.4%} | {fmt(elapsed)} + {fmt(remaining)} = {fmt(total_est)}"
#     except Exception:
#         return ""

# def _get_context() -> str:
#     """
#     Extrai o contexto de chamada dentro do projeto com base na stack trace.

#     Returns:
#         str: Caminho relativo no formato "line X of function() in path/file.py"
#     """
#     try:
#         stack = inspect.stack()
#         project_root = config.paths.root_dir
#         relevant = []

#         for frame in stack:
#             path = Path(frame.filename).resolve()
#             if project_root in path.parents:
#                 rel_path = path.relative_to(project_root)
#                 relevant.append(f"line {frame.lineno} of {frame.function}() in '{rel_path}'")

#         return " <- ".join(relevant[3:-1])  # Ignora a camada interna da função de log
#     except Exception:
#         return ""

# def log_message(message, name=None, level:str="debug", progress=None):
#     """
#     Registra uma mensagem no logger configurado com informações de progresso e stack trace.

#     Args:
#         message (str): A mensagem principal a ser registrada.
#         name (str, optional): Nome do logger. Se omitido, usa o nome do arquivo de log.
#         level (str): Nível de log. Pode ser: 'debug', 'info', 'warning', 'error', 'critical'.
#         progress (dict, optional): Dicionário com dados de progresso para log evolutivo.
#             - index (int): Índice atual do item.
#             - size (int): Tamanho total da sequência.
#             - start_time (float): Timestamp inicial (time.time()).

#     Exemplo:
#         log_message("Processando empresa X", level="info", progress={"index":3, "size":10, "start_time":t0})
#     """
#     logger = _get_logger(name, level=level)
#     progress_msg = _format_progress(progress) if progress else ""
#     context = _get_context()

#     # Adiciona contexto apenas para nível DEBUG
#     full_message = f"{message} | {context}" if level.lower() == "debug" else message
#     if progress_msg:
#         full_message += f" | {progress_msg}"

#     try:
#         log_fn = getattr(logger, level.lower(), logger.info)
#         log_fn(full_message)
#     except Exception as e:
#         print(f"Logging failed: {e}")




# # =============================================================================================================
# # def self.logger.log(message, name=None, level:str="debug", progress=None):
# #     """
# #     Logs a message both to the terminal (stdout) and a file, ensuring consistent formatting.

# #     This function is designed to be a singleton logger initializer. It sets up a logger instance only once,
# #     with both stream and file handlers, and logs the given message using the correct stack trace origin.

# #     Args:
# #         message (str): The actual message to be logged.
# #         name (str, optional): The name of the logger. If None, it is inferred from the log file name.
# #         level (str): Logging level for this message. One of: 'debug', 'info', 'warning', 'error', 'critical'.
# #         progress (dict): dict containing index: (of element in loop), size: (len of total elements) and start_time: (self_explaining)

# #     Returns:
# #         logging.Logger: The configured logger instance.
# #     """
# #     try:
# #         config = Config()
# #         log_path = config.paths["log_file"]
        
# #         # Resolve logger name
# #         name = name or Path(config.paths["log_file"]).stem

# #         global _logger_instance

# #         # Progress
# #         progress_msg = ""
# #         if progress:
# #             index = progress.get("index", 0)
# #             size = progress.get("size", 1)
# #             start = progress.get("start_time", time.time())
# #             now = time.time()

# #             completed = index + 1
# #             percent = (completed / size)
# #             elapsed = now - start
# #             avg = elapsed / completed
# #             remaining = (size - completed) * avg
# #             total_est = elapsed + remaining

# #             def fmt(seconds):
# #                 h, rem = divmod(int(seconds), 3600)
# #                 m, s = divmod(rem, 60)
# #                 return f"{h}h{m:02}m{s:02}s"

# #             progress_msg = (
# #                 f"{completed}/{size} | {percent:.1%} | "
# #                 f"{fmt(elapsed)} + {fmt(remaining)} = {fmt(total_est)} "
# #             )


# #         if _logger_instance is None:
# #             # Create and configure logger
# #             logger = logging.getLogger(name)
# #             logger.setLevel(logging.DEBUG)  # Always capture all levels; handlers will filter as needed

# #             # Define formatter with precise timestamp, origin and message layout
# #             formatter = logging.Formatter(
# #                     (progress_msg) +
# #                     "%(asctime)s "
# #                     "%(levelname)s: "
# #                     "%(message)s "
# #                     # "at line %(lineno)d of %(funcName)s() in %(filename)s "
# #                     # "PID: %(process)d - %(processName)s | "
# #                     # "Thread: %(thread)d - %(threadName)s | "
# #                     # "%(name)s | "
# #                     , datefmt="%Y-%m-%d %H:%M:%S"  # Removes milliseconds
# #                 )

# #             # StreamHandler (e.g., console output)
# #             stream_handler = logging.StreamHandler()
# #             stream_handler.setLevel(logging.DEBUG)
# #             stream_handler.setFormatter(formatter)

# #             # FileHandler (persistent output)
# #             file_handler = logging.FileHandler(log_path)
# #             file_handler.setLevel(logging.DEBUG)
# #             file_handler.setFormatter(formatter)

# #             # Register both handlers
# #             logger.addHandler(stream_handler)
# #             logger.addHandler(file_handler)

# #             _logger_instance = logger

# #         # Get relevant stack frames inside the project
# #         stack = inspect.stack()
# #         project_root = config.paths.root_dir
# #         relevant = []

# #         for frame in stack:
# #             path = Path(frame.filename).resolve()
# #             if project_root in path.parents:
# #                 relevant.append(f"line {frame.lineno} of {frame.function}() in '{path.relative_to(project_root)}'")

# #         # Format into single message
# #         context = " <- ".join(relevant[1:-1])
# #         full_message = message if level.lower() != "debug" else f"{message} | {context}"

# #         # Log the combined message using stacklevel of the topmost relevant frame
# #         _log_method = getattr(_logger_instance, level.lower(), _logger_instance.info)
# #         _log_method(full_message + progress_msg)

# #     except Exception as e:
# #         print(f"Logging error: {e}")

# #     return _logger_instance
