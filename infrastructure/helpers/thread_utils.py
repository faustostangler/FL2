import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > threading")
import threading
from infrastructure.config import Config


class WorkerThreadIdentifier:
    """
    Gera e mantém identificadores legíveis e exclusivos por thread no pool.

    Exemplo de identificador: "W1", "W2", ..., até o limite de max_workers definido no Config.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("threading.WorkerThreadIdentifier")

    def __init__(self, config: Config):
        """
        Inicializa o gerador com base no número máximo de workers permitidos.

        Args:
            config (Config): Configuração global da aplicação.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("WorkerThreadIdentifier __init__")
        self._max_workers = config.global_settings.max_workers or 1
        self._thread_local = threading.local()
        self._counter = iter(range(1, self._max_workers + 1))

    def get_worker_name(self) -> str:
        """
        Retorna um nome exclusivo de worker para a thread atual, reusado enquanto ela viver.

        Returns:
            str: Nome como "W1", "W2", etc.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("WorkerThreadIdentifier.get_worker_name")
        if not hasattr(self._thread_local, "worker_name"):
            self._thread_local.worker_name = f"W{next(self._counter)}"
        # return self._thread_local.worker_name
        return str(threading.get_ident())
