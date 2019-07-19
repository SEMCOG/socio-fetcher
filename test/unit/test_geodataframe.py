import pytest
import pickle
from socioFetcher.geodataframe import GeoDataFrame
import pandas as pd


class TestGeoDataFrame:

    @pytest.mark.parametrize('county, dataset',
                             [('Livingston,MI', 'BEA'),
                              ('Macomb,MI', 'bls'),
                              ('Oakland,MI', 'BEAGDP')
                              ])
    def test_init(self, county, dataset):
        geoDf = GeoDataFrame(county, dataset)
        assert geoDf.county == county
        assert geoDf.dataset == dataset
        assert isinstance(geoDf.DataFrame, pd.DataFrame)
        assert str(geoDf) == geoDf.county == county

    @pytest.fixture()
    def acs_data(self):
        with open("test/unit/unittestdata/ACSdata.pickle", "rb") as f:
            ACSdata = pickle.load(f)
        return ACSdata

    @pytest.fixture()
    def acs_expected(self):
        with open("test/unit/unittestdata/ACSdata_expected.pickle", "rb") as f:
            ACSdata_expected = pickle.load(f)
        return ACSdata_expected

    def test_ACSParser(self, acs_data, acs_expected):
        geoDf = GeoDataFrame('Livingston,MI', 'ACS')
        re = geoDf.ACSParser(acs_data, year="2010")
        assert re.equals(acs_expected)

    @pytest.fixture()
    def bea_data(self):
        with open("test/unit/unittestdata/BEAdata.pickle", "rb") as f:
            BEAdata = pickle.load(f)
        return BEAdata

    @pytest.fixture()
    def bea_expected(self):
        with open("test/unit/unittestdata/BEAdata_expected.pickle", "rb") as f:
            BEAdata_expected = pickle.load(f)
        return BEAdata_expected

    def test_BEAParser(self, bea_data, bea_expected):
        print(bea_expected)
        geoDf = GeoDataFrame('Livingston,MI', 'BEA')
        re = geoDf.BEAParser(bea_data, gdp=False)
        print(re)
        assert re.equals(bea_expected)

    @pytest.fixture()
    def bea_gdp_data(self):
        with open("test/unit/unittestdata/BEAGDPdata.pickle", "rb") as f:
            BEAGDPdata = pickle.load(f)
        return BEAGDPdata

    @pytest.fixture()
    def bea_gdp_expected(self):
        with open("test/unit/unittestdata/BEAGDPdata_expected.pickle", "rb") as f:
            BEAGDPdata_expected = pickle.load(f)
        return BEAGDPdata_expected

    def test_BEAGDPParser(self, bea_gdp_data, bea_gdp_expected):
        geoDf = GeoDataFrame('Ann Arbor Metro', 'BEAGDP')
        re = geoDf.BEAParser(bea_gdp_data, gdp=True)
        assert re.equals(bea_gdp_expected)

    @pytest.fixture()
    def bls_data(self):
        with open("test/unit/unittestdata/BLSdata.pickle", "rb") as f:
            BLSdata = pickle.load(f)
        return BLSdata

    @pytest.fixture()
    def bls_expected(self):
        with open("test/unit/unittestdata/BLSdata_expected.pickle", "rb") as f:
            BLSdata_expected = pickle.load(f)
        return BLSdata_expected

    def test_BLSParser(self, bls_data, bls_expected):
        geoDf = GeoDataFrame('Livingston,MI', 'BLS')
        re = geoDf.BLSParser(bls_data)
        assert re.equals(bls_expected)

    def test_load_ACS(self, acs_data, acs_expected):
        geoDf = GeoDataFrame("Livingston,MI", "ACS")
        assert geoDf.DataFrame.shape == (0, 0)
        geoDf.load(acs_data, source="ACS", year="2010")
        assert geoDf.DataFrame.equals(acs_expected)
        geoDf.load(acs_data, source="ACS", year="2011")
        acs_expected_2 = acs_expected.rename({"2010": "2011"}, axis="rows")
        assert geoDf.DataFrame.equals(pd.concat([acs_expected, acs_expected_2],
                                                axis=0, sort=True))

    def test_load_BLS(self, bls_data, bls_expected):
        geoDf = GeoDataFrame("Livingston,MI", "BLS")
        assert geoDf.DataFrame.shape == (0, 0)
        geoDf.load(bls_data, source="BLS")
        assert geoDf.DataFrame.iloc[:, 0].equals(
            bls_expected.sort_index(axis=0))
