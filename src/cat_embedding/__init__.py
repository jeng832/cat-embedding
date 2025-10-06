__version__ = "0.1.0"

def main():
    # Lazy import to avoid importing heavy modules at package import time
    from .__main__ import main as _main
    _main()

__all__ = ["main"]