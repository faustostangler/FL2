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
    data_cleaner = create_data_cleaner(config, logger)

    # Start CLI
    logger.log(
        "Start FLY",
        level="info",
    )

    # Entry point for the FLY CLI application.
    controller = CLIController(config=config, logger=logger, data_cleaner=data_cleaner)
    controller.run()

    # Finaliza a execução com uma mensagem de confirmação
    logger.log(
        "Finish FLY",
        level="info",
    )
