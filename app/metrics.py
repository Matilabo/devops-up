"""Cálculo de CPU y memoria a partir de la respuesta de `docker stats`.

Replica las fórmulas que usa el comando `docker stats` del CLI.
"""

MIB = 1024 * 1024


def cpu_percent(stats: dict) -> float:
    """Porcentaje de CPU usado entre la muestra actual y la anterior."""
    cpu = stats.get("cpu_stats", {})
    precpu = stats.get("precpu_stats", {})

    cpu_delta = (
        cpu.get("cpu_usage", {}).get("total_usage", 0)
        - precpu.get("cpu_usage", {}).get("total_usage", 0)
    )
    system_delta = cpu.get("system_cpu_usage", 0) - precpu.get("system_cpu_usage", 0)
    if cpu_delta <= 0 or system_delta <= 0:
        return 0.0

    online_cpus = (
        cpu.get("online_cpus")
        or len(cpu.get("cpu_usage", {}).get("percpu_usage") or [])
        or 1
    )
    return round(cpu_delta / system_delta * online_cpus * 100, 2)


def memory_usage(stats: dict) -> dict:
    """Memoria usada (sin caché de archivos), límite y porcentaje."""
    memory = stats.get("memory_stats", {})
    usage = memory.get("usage", 0)
    limit = memory.get("limit", 0)

    # cgroup v2 informa "inactive_file"; cgroup v1, "total_inactive_file".
    detail = memory.get("stats", {})
    cache = detail.get("inactive_file", detail.get("total_inactive_file", 0))
    if cache < usage:
        usage -= cache

    return {
        "memory_usage_mib": round(usage / MIB, 2),
        "memory_limit_mib": round(limit / MIB, 2),
        "memory_percent": round(usage / limit * 100, 2) if limit else 0.0,
    }
