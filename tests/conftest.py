import pytest

from api import API


@pytest.fixture
def api():
    return API()
