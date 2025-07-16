"""Command-line entry point for the FLY application."""

from infrastructure.config import Config
from infrastructure.factories import create_data_cleaner
from infrastructure.logging import Logger
from presentation import CLIAdapter


def main() -> None:
    """Initialize and run the FLY application via the command-line interface.

    This function executes the following startup sequence:
    - Instantiates the configuration object (``Config``).
    - Creates the main logger.
    - Creates the data cleaner component.
    - Instantiates the CLI controller with injected dependencies.
    - Starts the application logic by calling ``controller.start_fly()``.
    """
    config = Config()
    logger = Logger(config)

    try:
        logger.log("Start Project FLY", level="info")
        data_cleaner = create_data_cleaner(config, logger)
        controller = CLIAdapter(config=config, logger=logger, data_cleaner=data_cleaner)
        controller.start_fly()
        logger.log("Finish Project FLY", level="info")
    except Exception as e:  # pragma: no cover
        logger.log(f"Erro {e}", level="info", show_path=True)


if __name__ == "__main__":
    main()
