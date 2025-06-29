from __future__ import annotations
import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > save_strategy")

from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class SaveStrategy(Generic[T]):
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("save_strategy.SaveStrategy(Generic[T])")
    """Buffers items and flushes them via a callback."""

    def __init__(
        self,
        save_callback: Optional[Callable[[List[T]], None]] = None,
        threshold: int = 50,
    ) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SaveStrategy(Generic[T]).__init__")
        self.save_callback = save_callback or (lambda buffer: None)
        self.threshold = threshold
        self.buffer: List[T] = []

    def handle(self, item: Optional[T]) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SaveStrategy(Generic[T]).handle()")
        if item is None:
            return

        self.buffer.append(item)
        if len(self.buffer) >= self.threshold:
            self.flush()

    def flush(self) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SaveStrategy(Generic[T]).flush()")
        if self.buffer:
            self.save_callback(self.buffer)
            self.buffer.clear()

    def finalize(self) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SaveStrategy(Generic[T]).finalize()")
        self.flush()
