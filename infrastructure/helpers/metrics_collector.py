class MetricsCollector:
    """Collects network and processing byte counts."""

    def __init__(self) -> None:
        self._network_bytes = 0
        self._processing_bytes = 0

    def record_network_bytes(self, n: int) -> None:
        self._network_bytes += n

    def record_processing_bytes(self, n: int) -> None:
        self._processing_bytes += n

    @property
    def network_bytes(self) -> int:
        return self._network_bytes

    @property
    def processing_bytes(self) -> int:
        return self._processing_bytes

    def get_metrics(self, elapsed_time: float):
        from domain.ports.worker_pool_port import Metrics

        return Metrics(
            elapsed_time=elapsed_time,
            network_bytes=self._network_bytes,
            processing_bytes=self._processing_bytes,
        )
