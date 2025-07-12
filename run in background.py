"""Command-line entry point for the FLY application."""

from infrastructure.config import Config
from infrastructure.factories import create_data_cleaner
from infrastructure.logging import Logger
from presentation import CLIController

# Executa a aplicação principal se este arquivo for executado diretamente
if __name__ == "__main__":
    # Inicializa a configuração
    config = Config()
    logger = Logger(config)

    # Load CLI
    logger.log(
        "Run Project FLY",
        level="info",
    )

    # Load data_cleaner
    data_cleaner = create_data_cleaner(config, logger)

    # Entry point for the FLY CLI application.
    # logger.log("Instantiate controller", level="info")
    controller = CLIController(config=config, logger=logger, data_cleaner=data_cleaner)

    # Run Controller
    # logger.log("Call Method controller.start()", level="info")
    controller.start()
    # logger.log("End  Method controller.start()", level="info")

    # logger.log("End Instance controller", level="info")

    # Finaliza a execução com uma mensagem de confirmação
    logger.log(
        "Finish Project FLY",
        level="info",
    )
