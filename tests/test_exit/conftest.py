import os

import requests
from logzero import logger
from pytest import fixture


def check_slow_service() -> bool:
    try:
        resp = requests.get("http://localhost:8700")
        resp.raise_for_status()
        logger.debug("test_exit.py's slow_service is ready!")
        return True
    except Exception:
        logger.debug("test_exit.py's slow_service not yet ready, trying again.")
        return False


@fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yaml"
    )


@fixture(scope="class")
def slow_service(docker_services) -> None:
    docker_services.wait_until_responsive(
        timeout=30.0, pause=10, check=lambda: check_slow_service()
    )
