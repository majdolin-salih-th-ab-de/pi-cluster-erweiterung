import time


def timestamp():
    """Einfaches Zeitformat für Logs."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
