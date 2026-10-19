"""Genera tráfico sobre la API para poblar el dashboard de golden signals.

Mezcla requests válidas con algunas a contenedores inexistentes (404) para que
también haya errores que graficar. Solo usa la librería estándar.

Uso:
    python scripts/generar_trafico.py --url http://localhost:8000 --segundos 120 --rps 5
"""

import argparse
import json
import random
import time
import urllib.error
import urllib.request
from collections import Counter


def call(base_url: str, path: str) -> int:
    try:
        with urllib.request.urlopen(base_url + path, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except urllib.error.URLError:
        return 0


def list_container_names(base_url: str) -> list[str]:
    try:
        with urllib.request.urlopen(base_url + "/containers", timeout=10) as response:
            return [container["name"] for container in json.load(response)]
    except (urllib.error.URLError, ValueError):
        return []


def pick_path(names: list[str]) -> str:
    roll = random.random()
    if roll < 0.10:
        return "/containers/no-existe/stats"
    if roll < 0.20:
        return "/health"
    if roll < 0.50 or not names:
        return "/containers"
    return f"/containers/{random.choice(names)}/stats"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--segundos", type=int, default=60)
    parser.add_argument("--rps", type=float, default=5, help="requests por segundo")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    names = list_container_names(base_url)
    print(f"Contenedores encontrados: {names or 'ninguno'}")

    results = Counter()
    deadline = time.monotonic() + args.segundos
    while time.monotonic() < deadline:
        path = pick_path(names)
        status = call(base_url, path)
        results[status] += 1
        print(f"{status} {path}")
        time.sleep(1 / args.rps)

    print("\nResumen por código HTTP (0 = sin conexión):")
    for status, count in sorted(results.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
