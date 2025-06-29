import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > byte_formatter")
class ByteFormatter:
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("byte_formatter class ByteFormatter")

    def format_bytes(self, bytes_amount: int) -> str:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("ByteFormatter.format_bytes()")

        if bytes_amount < 1024:
            return f"{bytes_amount:.2f}B"
        elif bytes_amount < 1024 ** 2:
            return f"{bytes_amount / 1024:.2f}KB"
        elif bytes_amount < 1024 ** 3:
            return f"{bytes_amount / (1024 ** 2):.2f}MB"
        else:
            return f"{bytes_amount / (1024 ** 3):.2f}GB"
