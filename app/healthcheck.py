"""Healthcheck del contenedor: `python -m app.healthcheck` sale con 0 si /health responde."""

import os
import sys
import urllib.request


def main() -> int:
    url = f"http://127.0.0.1:{os.getenv('PORT', '8000')}/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return 0 if response.status == 200 else 1
    except OSError:
        return 1


if __name__ == "__main__":
    sys.exit(main())
