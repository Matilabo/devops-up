from app.metrics import MIB, cpu_percent, memory_usage


def make_cpu_stats(total, precpu_total, system, precpu_system, online_cpus=2):
    return {
        "cpu_stats": {
            "cpu_usage": {"total_usage": total},
            "system_cpu_usage": system,
            "online_cpus": online_cpus,
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": precpu_total},
            "system_cpu_usage": precpu_system,
        },
    }


def test_cpu_percent_usa_la_formula_de_docker_stats():
    stats = make_cpu_stats(total=300, precpu_total=100, system=2000, precpu_system=1000)

    # (200 / 1000) * 2 cpus * 100
    assert cpu_percent(stats) == 40.0


def test_cpu_percent_es_cero_sin_variacion():
    stats = make_cpu_stats(total=100, precpu_total=100, system=2000, precpu_system=1000)

    assert cpu_percent(stats) == 0.0


def test_cpu_percent_cuenta_cpus_por_percpu_usage():
    stats = make_cpu_stats(total=300, precpu_total=100, system=2000, precpu_system=1000)
    stats["cpu_stats"]["online_cpus"] = None
    stats["cpu_stats"]["cpu_usage"]["percpu_usage"] = [1, 1, 1, 1]

    assert cpu_percent(stats) == 80.0


def test_cpu_percent_tolera_respuesta_vacia():
    assert cpu_percent({}) == 0.0


def test_memoria_descuenta_cache_en_cgroup_v2():
    stats = {
        "memory_stats": {
            "usage": 150 * MIB,
            "limit": 1000 * MIB,
            "stats": {"inactive_file": 50 * MIB},
        }
    }

    assert memory_usage(stats) == {
        "memory_usage_mib": 100.0,
        "memory_limit_mib": 1000.0,
        "memory_percent": 10.0,
    }


def test_memoria_descuenta_cache_en_cgroup_v1():
    stats = {
        "memory_stats": {
            "usage": 300 * MIB,
            "limit": 1000 * MIB,
            "stats": {"total_inactive_file": 100 * MIB},
        }
    }

    assert memory_usage(stats)["memory_usage_mib"] == 200.0


def test_memoria_sin_limite_devuelve_porcentaje_cero():
    assert memory_usage({})["memory_percent"] == 0.0
