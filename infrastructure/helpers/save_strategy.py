"""Provide buffering logic for saving batches of items."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Callable, Generic, List, Optional, TypeVar, Union

from infrastructure.config import Config

T = TypeVar("T")


class SaveStrategy(Generic[T]):
    """Buffers items and flushes them via a callback."""

    def __init__(
        self,
        save_callback: Optional[Callable[[List[T]], None]] = None,
        threshold: Optional[int] = None,
        config: Optional[Config] = None,
    ) -> None:
        """Create a new strategy instance.

        Args:
            save_callback: Function invoked when the buffer is flushed.
            threshold: Number of items to collect before flushing.
            config: Configuration object used when ``threshold`` is not
                provided.
        """
        self.config = config
        self.save_callback = save_callback or (lambda buffer: None)
        self.threshold = threshold or (
            config.global_settings.threshold if config else 50
        )
        self.buffer: List[T] = []

    def handle(
        self, item: Optional[Union[T, Iterable[T]]], remaining: Optional[int] = None
    ) -> None:
        """Add one or more items to the buffer and flush when ``threshold`` is
        reached.

        Args:
            item: Single item or iterable of items to add to the buffer.
            remaining: Number of items left to process. If provided, the buffer
                flushes when this value is a multiple of ``threshold`` or zero.
        """
        if item is None:
            return

        if remaining is None and self.config:
            remaining = self.config.global_settings.threshold

        if isinstance(item, Iterable):
            self.buffer.extend(item)
        else:
            self.buffer.append(item)

        flush_by_remaining = False
        if remaining is not None:
            flush_by_remaining = remaining % self.threshold == 0

        should_flush = len(self.buffer) >= self.threshold or flush_by_remaining

        if remaining == 0 or should_flush:
            self.flush()

    def flush(self) -> None:
        """Invoke the callback with all buffered items and clear the buffer."""
        if self.buffer:
            self.save_callback(self.buffer)
            self.buffer.clear()

    def finalize(self) -> None:
        """Flush any remaining items at the end of processing."""
        self.flush()
