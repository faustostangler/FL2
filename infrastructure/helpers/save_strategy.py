from __future__ import annotations

from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class SaveStrategy(Generic[T]):
    """Buffers items and flushes them via a callback."""

    def __init__(
        self,
        save_callback: Optional[Callable[[List[T]], None]] = None,
        threshold: int = 50,
    ) -> None:
        """Create a new strategy instance.

        Args:
            save_callback: Function invoked when the buffer is flushed.
            threshold: Number of items to collect before flushing.
        """
        self.save_callback = save_callback or (lambda buffer: None)
        self.threshold = threshold
        self.buffer: List[T] = []

    def handle(self, item: Optional[T]) -> None:
        """Add ``item`` to the buffer and flush when ``threshold`` is reached."""

        if item is None:
            return

        self.buffer.append(item)
        if len(self.buffer) >= self.threshold:
            self.flush()

    def flush(self) -> None:
        """Invoke the callback with all buffered items and clear the buffer."""

        if self.buffer:
            self.save_callback(self.buffer)
            self.buffer.clear()

    def finalize(self) -> None:
        """Flush any remaining items at the end of processing."""

        self.flush()
