import pytest
from google.cloud import datastore
from xprocess import ProcessStarter

# Globals
DATASTORE_PROJECT_ID = "dummy-project"


@pytest.fixture(scope="session")
def datastore_server(xprocess):
    class Starter(ProcessStarter):
        # startup pattern
        pattern = "Local Datastore initialized"

        # command to start process
        args = [
            "gcloud",
            "beta",
            "emulators",
            "datastore",
            "start",
            "--project=dummy-project",
            "--consistency=1.0",
            "--no-store-on-disk",
            "--host-port=localhost:8001",
        ]

    # ensure process is running and return its logfile
    _ = xprocess.ensure("myserver", Starter)

    conn = {"host": "localhost", "port": 8001}
    yield conn

    # clean up whole process tree afterwards
    xprocess.getinfo("myserver").terminate()


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


@pytest.mark.local_datastore
def test_datastore_empty(datastore_server):
    client = datastore.Client()
    key = client.key("EntityKind", 1234)
    result = client.get(key)
    assert result is None


# Example from https://pypi.org/project/google-cloud-datastore/#example-usage
@pytest.mark.local_datastore
def test_datastore_store(datastore_server):
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
