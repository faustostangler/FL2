from dataclasses import dataclass

from domain.ports.worker_pool_port import Metrics


@dataclass
class MetricsCollector:
    """Collects network and processing byte metrics."""

    network_bytes: int = 0
    processing_bytes: int = 0

    def record_network_bytes(self, amount: int) -> None:
        """Accumulate bytes retrieved from network calls."""
        self.network_bytes += amount

    def record_processing_bytes(self, amount: int) -> None:
        """Accumulate bytes produced during processing."""
        self.processing_bytes += amount

    def snapshot(self, elapsed_time: float) -> Metrics:
        """Return a Metrics dataclass populated with current counts."""
        return Metrics(
            elapsed_time=elapsed_time,
            network_bytes=self.network_bytes,
            processing_bytes=self.processing_bytes,
        )
