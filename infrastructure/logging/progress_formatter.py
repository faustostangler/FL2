import time


class ProgressFormatter:
    """
    Responsável por formatar informações de progresso para logs.
    """

    def format(self, progress: dict) -> str:
        """
        Gera uma string como: "15/100 | 15.00% | 0h00m10s + 0h01m00s = 0h01m10s"
        """
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

            return f"{completed}/{size} | {percent:.2%} | {fmt(elapsed)} + {fmt(remaining)} = {fmt(total_est)}"
        except Exception:
            return ""
