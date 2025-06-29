import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > progress_formatter")
import time


class ProgressFormatter:
    """Format progress information for logging."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("progress_formatter.ProgressFormatter")

    def format(self, progress: dict) -> str:
        """Return a formatted progress string like ``"15/100 | 15.00% | 0h00m10s + 0h01m00s = 0h01m10s"``."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("ProgressFormatter.format()")
        try:
            index = progress.get("index", 0)
            size = progress.get("size", 1)
            start = progress.get("start_time", time.time())
            now = time.time()

            completed = index + 1
            percent = completed / size
            elapsed = now - start
            avg = elapsed / completed
            remaining = (size - completed) * avg
            total_est = elapsed + remaining

            def fmt(seconds):
                h, rem = divmod(int(seconds), 3600)
                m, s = divmod(rem, 60)
                return f"{h}h{m:02}m{s:02}s"

            base = f"{size - completed}+{completed}={size} | {percent:.2%} | {fmt(remaining)} + {fmt(elapsed)} = {fmt(total_est)}"

            extra_info = progress.get("extra_info", [])
            if isinstance(extra_info, list):
                extra_str = " ".join(str(e) for e in extra_info if e)
                return f"{base} | {extra_str}" if extra_str else base
            return base
        except Exception:
            return ""
