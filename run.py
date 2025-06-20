from infrastructure.config import Config
from infrastructure.logging import Logger
from presentation import CLIController

# Executa a aplicação principal se este arquivo for executado diretamente
if __name__ == "__main__":
    # Inicializa a configuração
    config = Config()
    logger = Logger(config)
    
    # Start CLI
    logger.log("Start FLY", level="info")

    # Entry point for the FLY CLI application.
    controller = CLIController(config, logger)
    controller.run()

# Finaliza a execução com uma mensagem de confirmação
print("done")