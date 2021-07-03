# PyTest and GCP Datastore Emulation

_Work in progress_.

Aim is to run GCP Datastore emulation as part of pytest somehow.


* [tox-docker](https://github.com/tox-dev/tox-docker/) doesn't seem to work
  because we cannot set [arbitrary commands](https://github.com/tox-dev/tox-docker/issues/91)
* [pytest-docker-py](https://github.com/jameshnsears/pytest-docker-py) seems promising,
  and it's easy to use indeed, but need to start up a new container every time for
  a new test, and cannot keep one around (using e.g. the `scope="session"` setup of the
  fixtures). Also need to do the health-check ourselves there (and because of the automatic
  setup, have to do it in each test).
* Could do instead self-rolled PyTest fixture that is scoped to the session/module, and
  thus a multiple tests can be run on a single setup... More manual and likely error-prone,
  but the best fit?
* Could also adjust the fixtures to automatically preload some data? As in [fixtures requesting other fixtures](https://docs.pytest.org/en/latest/how-to/fixtures.html#fixtures-can-request-other-fixtures)?
* [`test_docker.py`](test_docker.py) implements tests with external Docker image spun up
* [`test_external.py`](test_external.py) implements tests with emulator process spun up (when `gcloud` and the relevant components are installed locally)

Ideally this is combined with `tox` to run a proper testing environment.
