"""Command-line entry point for the FLY application."""

from infrastructure.config import Config
from infrastructure.factories import create_data_cleaner
from infrastructure.logging import Logger
from presentation import CLIAdapter


def main() -> None:
    """Inicializa e executa a aplicação FLY pela interface de linha de comando (CLI).

    Esta função realiza a sequência de inicialização dos componentes principais:
    - Instancia o objeto de configuração (`Config`).
    - Cria o logger principal.
    - Cria o componente de limpeza de dados.
    - Instancia o controlador CLI com as dependências injetadas.
    - Inicia o processo principal da aplicação via `controller.start_fly()`.
    """
    # Inicializa a configuração
    config = Config()
    logger = Logger(config)

    # Load CLI
    logger.log(
        "Start Project FLY",
        level="info",
    )

    # Load data_cleaner
    data_cleaner = create_data_cleaner(config, logger)

    # Entry point for the FLY CLI application.
    # logger.log("Instantiate controller", level="info")
    controller = CLIAdapter(config=config, logger=logger, data_cleaner=data_cleaner)

    # Run Controller
    # logger.log("Call Method controller.start()", level="info")
    controller.start_fly()
    # logger.log("End  Method controller.start()", level="info")

    # logger.log("End Instance controller", level="info")

    # Finaliza a execução com uma mensagem de confirmação
    logger.log(
        "Finish Project FLY",
        level="info",
    )

# Executa a aplicação principal se este arquivo for executado diretamente
if __name__ == "__main__":
    main()
