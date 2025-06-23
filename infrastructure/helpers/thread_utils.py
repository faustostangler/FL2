import threading
from infrastructure.config import Config


class WorkerThreadIdentifier:
    """
    Gera e mantém identificadores legíveis e exclusivos por thread no pool.

    Exemplo de identificador: "W1", "W2", ..., até o limite de max_workers definido no Config.
    """

    def __init__(self, config: Config):
        """
        Inicializa o gerador com base no número máximo de workers permitidos.

        Args:
            config (Config): Configuração global da aplicação.
        """
        self._max_workers = config.global_settings.max_workers or 1
        self._thread_local = threading.local()
        self._counter = iter(range(1, self._max_workers + 1))

    def get_worker_name(self) -> str:
        """
        Retorna um nome exclusivo de worker para a thread atual, reusado enquanto ela viver.

        Returns:
            str: Nome como "W1", "W2", etc.
        """
        if not hasattr(self._thread_local, "worker_name"):
            self._thread_local.worker_name = f"{next(self._counter)}"
        return str(threading.get_ident())
