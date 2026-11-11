import pytest
from prefect.testing.utilities import prefect_test_harness


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    """
    Ensures Prefect uses a temporary local SQLite database for testing,
    preventing it from communicating with your real Prefect server/cloud.
    Runs once per test session.
    """
    with prefect_test_harness():
        yield
