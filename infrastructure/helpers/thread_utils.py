import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > threading")
import threading
from infrastructure.config import Config


class WorkerThreadIdentifier:
    """Generate readable, unique identifiers for worker threads.

    Example identifiers: ``"W1"``, ``"W2"``, up to the ``max_workers`` limit from ``Config``.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("threading.WorkerThreadIdentifier")

    def __init__(self, config: Config):
        """Initialize the generator using the configured ``max_workers`` value.

        Args:
            config: Application configuration with ``max_workers``.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("WorkerThreadIdentifier.__init__")
        self._max_workers = config.global_settings.max_workers or 1
        self._thread_local = threading.local()
        self._counter = iter(range(1, self._max_workers + 1))

    def get_worker_name(self) -> str:
        """Return a unique worker name for the current thread.

        Returns:
            str: A name such as ``"W1"`` or ``"W2"`` reused while the thread lives.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("WorkerThreadIdentifier.get_worker_name")
        if not hasattr(self._thread_local, "worker_name"):
            self._thread_local.worker_name = f"W{next(self._counter)}"
        # return self._thread_local.worker_name
        return str(threading.get_ident())
