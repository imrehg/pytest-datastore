import pytest

@pytest.fixture(scope="session")
def resource():
    print("setup")
    yield "resource"
    print("teardown")

# class TestResource:
#     def test_that_depends_on_resource(self, resource):
#         print("testing {}".format(resource))

def test_that_doesnt_depends_on_resource():
    print("testing0 {}".format(""))

def test_that_depends_on_resource(resource):
    print("testing1 {}".format(resource))

def test_another_depends_on_resource(resource):
    print("testing2 {}".format(resource))
