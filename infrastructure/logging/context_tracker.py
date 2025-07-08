import inspect
from pathlib import Path


class ContextTracker:
    """Extracts the call origin within the project for debugging logs."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def get_context(self) -> str:
        """Return a string like ``"line X of func() in 'path/file.py' <-
        ..."``."""
        try:
            stack = inspect.stack()
            relevant = []

            for frame in stack:
                path = Path(frame.filename).resolve()
                if self.project_root in path.parents:
                    rel_path = path.relative_to(self.project_root)
                    relevant.append(
                        f"line {frame.lineno} of {frame.function}() in '{rel_path}'"
                    )

            return " <- ".join(relevant[3:-1])
        except Exception:
            return ""
