import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > metrics_collector")
class MetricsCollector:
    """Collects network and processing byte counts."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("metrics_collector class MetricsCollector")

    def __init__(self) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector __init__")
        self._network_bytes = 0
        self._processing_bytes = 0

    def record_network_bytes(self, n: int) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector.record_network_bytes()")
        self._network_bytes += n

    def record_processing_bytes(self, n: int) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector.record_processing_bytes()")
        self._processing_bytes += n

    @property
    def network_bytes(self) -> int:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector.network_bytes()")
        return self._network_bytes

    @property
    def processing_bytes(self) -> int:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector.processing_bytes()")
        return self._processing_bytes

    def get_metrics(self, elapsed_time: float):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("MetricsCollector.get_metrics()")
        from domain.ports.worker_pool_port import Metrics

        return Metrics(
            elapsed_time=elapsed_time,
            network_bytes=self._network_bytes,
            processing_bytes=self._processing_bytes,
        )
