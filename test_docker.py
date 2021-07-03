import time

import docker
import pytest
from google.cloud import datastore

# Globals
DATASTORE_PROJECT_ID = "dummy-project"


# From docker-py source code (with some changes)
# https://github.com/docker/docker-py/blob/650aad3a5fb84059b392ad450f760ed08143ae3f/tests/helpers.py#L80-L85
def _wait_on_condition(condition, delay=0.1, timeout=40):
    start_time = time.monotonic()
    while not condition():
        if time.monotonic() - start_time > timeout:
            raise AssertionError("Timeout: %s" % condition)
        time.sleep(delay)


# From docker-py source code
# https://github.com/docker/docker-py/blob/650aad3a5fb84059b392ad450f760ed08143ae3f/tests/integration/api_healthcheck_test.py#L7
def _wait_on_health_status(client, container, status):
    def condition():
        res = client.inspect_container(container)
        return res["State"]["Health"]["Status"] == status

    return _wait_on_condition(condition, delay=1, timeout=15)


@pytest.fixture(scope="session")
def datastore_container(request):
    """Set up an emulated Datastore with the gcloud CLI
    inside a Docker container.
    """
    SECOND = 1_000_000_000
    client = docker.from_env()
    container = client.containers.create(
        "google/cloud-sdk:latest",
        (
            "gcloud beta emulators datastore start"
            f" --project={DATASTORE_PROJECT_ID}"
            " --consistency=1.0"
            " --no-store-on-disk"
            " --host-port=0.0.0.0:8001"
        ),
        ports={"8001/tcp": 8001},
        auto_remove=True,
        healthcheck=dict(
            test="curl --fail localhost:8001",
            interval=5 * SECOND,
            timeout=5 * SECOND,
            retries=3,
            start_period=5 * SECOND,
        ),
    )
    container.start()

    # Explicit finalizer to do proper cleanup if the healthy state not reached
    def stop_container():
        container.stop()

    request.addfinalizer(stop_container)

    # wait until healthy status is achieved, ie. the runnin datastore answers
    _wait_on_health_status(docker.APIClient(), container.id, "healthy")

    return container


@pytest.fixture(autouse=True)
def datastore_env_setup(monkeypatch):
    """Set up all relevant Datastore env variables to be used
    with emulation.
    """
    monkeypatch.setenv("DATASTORE_EMULATOR_HOST", "localhost:8001")
    monkeypatch.setenv("DATASTORE_PROJECT_ID", DATASTORE_PROJECT_ID)
    monkeypatch.setenv("DATASTORE_DATASET", DATASTORE_PROJECT_ID)
    monkeypatch.setenv(
        "DATASTORE_EMULATOR_HOST_PATH", "localhost:8001/datastore"
    )
    monkeypatch.setenv("DATASTORE_HOST", "http://localhost:8001")


# Setup done, tests start below


@pytest.mark.docker
def test_datastore_empty(datastore_container):
    client = datastore.Client()
    key = client.key("EntityKind", 1234)
    result = client.get(key)
    assert result is None


# Example from https://pypi.org/project/google-cloud-datastore/#example-usage
@pytest.mark.docker
def test_datastore_store(datastore_container):
    # Create, populate and persist an entity with keyID=1234
    client = datastore.Client()
    key = client.key("EntityKind", 1234)
    entity = datastore.Entity(key=key)
    entity.update(
        {
            "foo": "bar",
            "baz": 1337,
            "qux": False,
        }
    )
    client.put(entity)
    # Then get by key for this entity
    result = client.get(key)
    assert result == entity
