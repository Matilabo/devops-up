"""Errores del servicio de contenedores con su código HTTP asociado."""


class ContainerServiceError(Exception):
    status_code = 500


class DockerUnavailableError(ContainerServiceError):
    status_code = 503

    def __init__(self):
        super().__init__("No se pudo conectar con el demonio de Docker")


class ContainerNotFoundError(ContainerServiceError):
    status_code = 404

    def __init__(self, ref: str):
        super().__init__(f"No existe el contenedor '{ref}'")


class ContainerNotRunningError(ContainerServiceError):
    status_code = 409

    def __init__(self, ref: str):
        super().__init__(f"El contenedor '{ref}' no está en ejecución")


class ContainerOperationError(ContainerServiceError):
    status_code = 502

    def __init__(self, detail: str):
        super().__init__(f"Docker rechazó la operación: {detail}")
