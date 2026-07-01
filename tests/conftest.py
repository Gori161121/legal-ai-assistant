import pytest

from backend.data_loader import load_data, load_knowledge_base


@pytest.fixture(scope="session")
def data():
    return load_data()


@pytest.fixture(scope="session")
def kb():
    return load_knowledge_base()
