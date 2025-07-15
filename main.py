"""Command-line entry point for the FLY application."""

from infrastructure.config import Config
from infrastructure.factories import create_data_cleaner
from infrastructure.logging import Logger
from presentation import CLIAdapter


def main() -> None:
    """Initialize and run the FLY application via the command-line interface (CLI).

    This function executes the following startup sequence:
    - Instantiates the configuration object (`Config`).
    - Creates the main logger.
    - Creates the data cleaner component.
    - Instantiates the CLI controller with injected dependencies.
    - Starts the application logic by calling `controller.start_fly()`.
    """
    # Initialize application configuration
    config = Config()
    logger = Logger(config)

    # Load CLI
    logger.log(
        "Start Project FLY",
        level="info",
    )

    # Load data_cleaner
    data_cleaner = create_data_cleaner(config, logger)

    # Entry point for the FLY CLI application
    # logger.log("Instantiate controller", level="info")
    controller = CLIAdapter(config=config, logger=logger, data_cleaner=data_cleaner)

    # Run Controller
    # logger.log("Call Method controller.start()", level="info")
    controller.start_fly()
    # logger.log("End  Method controller.start()", level="info")

    # logger.log("End Instance controller", level="info")

    # Finalize execution with a confirmation message
    logger.log(
        "Finish Project FLY",
        level="info",
    )


# Run main function if this script is executed directly
if __name__ == "__main__":
    main()
