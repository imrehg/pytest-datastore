import docker
import pytest
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

@pytest.fixture(scope="module")
def dockerpy_easy_to_use():
    return [{'image': 'google/cloud-sdk:latest',
             'name': 'gcloud',
             'ports': {'8001/tcp': 8001},
             'command': 'gcloud beta emulators datastore start --no-store-on-disk --project=dummy-project --host-port=0.0.0.0:8001'}
            ]


@pytest.mark.timeout(60)
def test_plugin(dockerpy_easy_to_use):
    """
    For each test_ def, when a fixture starting with 'dockerpy' is supplied, the plugin overrides pytest's setup and teardown.
    pytest_runtest_setup = will pull / start container(s).
    pytest_runtest_teardown = will kill container(s).
    """

    assert dockerpy_easy_to_use is not None

    # Wait until things start up
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    r = s.get("http://localhost:8001")
    assert r.status_code == 200

    client = docker.from_env()
    container_found = False
    for container in client.containers.list():
        for tag in container.image.tags:
            if tag == 'google/cloud-sdk:latest':
                container_found = True

    time.sleep(10)
    assert container_found

@pytest.mark.timeout(60)
def test_again(dockerpy_easy_to_use):
    """
    For each test_ def, when a fixture starting with 'dockerpy' is supplied, the plugin overrides pytest's setup and teardown.
    pytest_runtest_setup = will pull / start container(s).
    pytest_runtest_teardown = will kill container(s).
    """

    assert dockerpy_easy_to_use is not None

    # Wait until things start up
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    r = s.get("http://localhost:8001")
    assert r.status_code == 200

    client = docker.from_env()
    container_found = False
    for container in client.containers.list():
        for tag in container.image.tags:
            if tag == 'google/cloud-sdk:latest':
                container_found = True

    time.sleep(10)
    assert container_found

