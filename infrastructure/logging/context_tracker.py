import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > context_tracker")
import inspect
from pathlib import Path


class ContextTracker:
    """
    Extrai a origem da chamada no projeto para logs de depuração.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("context_tracker.ContextTracker")

    def __init__(self, project_root: Path):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("ContextTracker.__init__")

        self.project_root = project_root

    def get_context(self) -> str:
        """
        Retorna string no formato:
        "line X of func() in 'relative/path/file.py' <- ..."
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("ContextTracker.get_context()")
        try:
            stack = inspect.stack()
            relevant = []

            for frame in stack:
                path = Path(frame.filename).resolve()
                if self.project_root in path.parents:
                    rel_path = path.relative_to(self.project_root)
                    relevant.append(f"line {frame.lineno} of {frame.function}() in '{rel_path}'")

            return " <- ".join(relevant[3:-1])
        except Exception:
            return ""
