import pytest

from api import API


@pytest.fixture
def api():
    return API()


@pytest.fixture
def base_url():
    return "http://testserver"

@pytest.fixture
def client(api):
    return api.test_session()