import pytest
from dynaconf import settings  # type: ignore[import-untyped]


@pytest.fixture(scope="session", autouse=True)
def set_test_settings() -> None:
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
