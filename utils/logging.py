_logger_instance = None

def log_message(message, name=None, level:str="debug"):
    """
    Logs a message both to the terminal (stdout) and a file, ensuring consistent formatting.

    This function is designed to be a singleton logger initializer. It sets up a logger instance only once,
    with both stream and file handlers, and logs the given message using the correct stack trace origin.

    Args:
        log_path (str or Path, optional): The path to the log file. If None, it uses the default from Config.
        name (str, optional): The name of the logger. If None, it is inferred from the log file name.
        level (str): Logging level for this message. One of: 'debug', 'info', 'warning', 'error', 'critical'.
        message (str): The actual message to be logged.

    Returns:
        logging.Logger: The configured logger instance.
    """
    try:
        from config.config import Config
        from pathlib import Path
        import logging
        import inspect

        config = Config()
        log_path = config.paths["log_file"]
        
        # Resolve logger name
        name = name or Path(config.paths["log_file"]).stem

        global _logger_instance

        if _logger_instance is None:
            # Create and configure logger
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)  # Always capture all levels; handlers will filter as needed

            if not logger.handlers:
                # Define formatter with precise timestamp, origin and message layout
                formatter = logging.Formatter(
                    "%(asctime)s "
                    "%(levelname)s: "
                    "%(message)s "
                    # "at line %(lineno)d of %(funcName)s() in %(filename)s "
                    # "PID: %(process)d - %(processName)s | "
                    # "Thread: %(thread)d - %(threadName)s | "
                    # "%(name)s | "
                    , datefmt="%Y-%m-%d %H:%M:%S"  # Removes milliseconds
                )

                # StreamHandler (e.g., console output)
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.DEBUG)
                stream_handler.setFormatter(formatter)

                # FileHandler (persistent output)
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)

                # Register both handlers
                logger.addHandler(stream_handler)
                logger.addHandler(file_handler)

            _logger_instance = logger

        # Get relevant stack frames inside the project
        stack = inspect.stack()
        project_root = config.paths["root_folder"]
        relevant = []

        for frame in stack:
            path = Path(frame.filename).resolve()
            if project_root in path.parents:
                relevant.append(f"line {frame.lineno} of {frame.function}() in '{path.relative_to(project_root)}'")

        # Format into single message
        context = " < ".join(relevant[1:-1])
        full_message = f"{message} | {context}"

        # Log the combined message using stacklevel of the topmost relevant frame
        _log_method = getattr(_logger_instance, level.lower(), _logger_instance.info)
        _log_method(full_message)

    except Exception as e:
        print(f"Logging error: {e}")

    return _logger_instance
