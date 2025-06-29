import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > logger")
import logging
import uuid
from typing import Optional

from infrastructure.config.config import Config
from infrastructure.logging.progress_formatter import ProgressFormatter
from infrastructure.logging.context_tracker import ContextTracker


class Logger:
    """Application logger wrapping Python's ``logging`` module."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("logger.Logger")

    def __init__(self, config: Config, level: str = "DEBUG", logger_name: Optional[str] = None):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("Logger.__init__")
        self._run_id = uuid.uuid4().hex[:8]
        self.worker_id = uuid.uuid4().hex[:8]

        self.config = config
        self.logger_name = logger_name or self.config.global_settings.app_name or "FLY"
        self.progress_formatter = ProgressFormatter()
        self.context_tracker = ContextTracker(config.paths.root_dir)
        self._logger = self._setup_logger(level)

    def _setup_logger(self, level: str) -> logging.LoggerAdapter:
        """Configure the underlying ``logging`` logger with console and file handlers."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("Logger.setup_logger()")
        log_path = self.config.logging.full_path
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            formatter = SafeFormatter(
                "%(run_id)s %(worker_id)s %(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            sh = logging.StreamHandler()
            sh.setLevel(getattr(logging, level.upper(), logging.INFO))
            sh.setFormatter(formatter)
            logger.addHandler(sh)

            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        adapter = MergedLoggerAdapter(logger, extra={"run_id": self._run_id})

        return adapter

    def log(self, message: str, level: str = "info", progress: Optional[dict] = None, extra: Optional[dict] = None, worker_id: Optional[str] = None):
        """Log a message with optional progress and context information."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("Logger.log()")
        context_msg = self.context_tracker.get_context() if level.lower() == "debug" else ""
        progress_msg = self.progress_formatter.format(progress) if progress else ""

        full_message = message
        if progress_msg:
            full_message += f" | {progress_msg}"
        if context_msg:
            full_message += f" | {context_msg}"

        if extra:
            extra_str = " ".join(
                    str(v)
                    for v in extra.values()
                    if v not in (None, "")
                )
            full_message += f" | {extra_str}"

        try:
            log_fn = getattr(self._logger, level.lower(), self._logger.info)
            merged_extra = {
                "run_id":    self._run_id,
                "worker_id": worker_id or self.worker_id,
            }

            log_fn(full_message, extra=merged_extra)
        except Exception as e:
            print(f"Logging failed: {e} - {full_message}")


class SafeFormatter(logging.Formatter):
    """Formatter that injects default values for missing log attributes."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("logger.SafeFormatter")
    def format(self, record):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SafeFormatter.format()")

        # Define valores padrão
        defaults = {
            "run_id": "0",
            "worker_id": "0", 
        }

        for key, default in defaults.items():
            if not hasattr(record, key) or not getattr(record, key):
                setattr(record, key, default)

        return super().format(record)


class MergedLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that merges ``extra`` dictionaries from calls and defaults."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("logger.MergedLoggerAdapter")
    def process(self, msg, kwargs):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MergedLoggerAdapter.process()")
        base = self.extra if isinstance(self.extra, dict) else {}
        extra = kwargs.get("extra") or {}
        if not isinstance(extra, dict):
            extra = {}
        kwargs["extra"] = {**base, **extra}
        return msg, kwargs
