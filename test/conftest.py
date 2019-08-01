import pytest
from socioFetcher.config import Config


@pytest.fixture()
def BLS_TEST_API_KEY():
    return "5a0e1a49d56d402d8331feac501593dd"


@pytest.fixture()
def BEA_TEST_API_KEY():
    return "4040651D-C3D5-4A2F-AEE5-23CD52AF863C"


@pytest.fixture()
def CENSUS_TEST_API_KEY():
    return "a1b79f5105b689bd9c4ed357de83130393b6dec7"


@pytest.fixture()
def config(BLS_TEST_API_KEY, BEA_TEST_API_KEY, CENSUS_TEST_API_KEY):
    config = Config()
    config.BLS.API_KEY = BLS_TEST_API_KEY
    config.BEA.API_KEY = BEA_TEST_API_KEY
    config.Census.API_KEY = CENSUS_TEST_API_KEY
    return config
