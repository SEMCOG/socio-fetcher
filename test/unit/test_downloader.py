import pytest
import itertools
from socioFetcher.downloader import Downloader
from socioFetcher.config import config


class TestDownloader:
    @pytest.mark.parametrize('dataset, fipsList', [
        (['BEA', 'BLS', 'ACS'], ["26093"]),
        (['BEA', 'BLS'], ["26093"]),
        (['BEA'], ["26093"]),
        (['BEA-GDP'], ["11460"])
    ])
    def test_init_dataset(self, dataset, fipsList):
        downloader = Downloader(dataset, fipsList)
        assert downloader.dataset == dataset
        assert downloader.fipsList == fipsList
        assert downloader.data == {fips: {} for fips in fipsList}
        assert downloader.config == config

    def test_init_dataset_get_raise(self):
        with pytest.raises(TypeError):
            Downloader([], ["26093"])
        with pytest.raises(TypeError):
            Downloader("BEA", ["26093"])
        with pytest.raises(ValueError):
            Downloader(["INVALID"], ["26093"])
        with pytest.raises(ValueError):
            Downloader(["BEA", "BEA-GDP"], ["11460"])

    def test_init_fipsList_get_raise(self):
        with pytest.raises(TypeError):
            Downloader(["BEA", "BLS"], [])
        with pytest.raises(TypeError):
            Downloader(["BEA", "BLS"], "26093")
        with pytest.raises(ValueError):
            Downloader(["BEA", "BLS"], ["00000"])

    def test_getBLSSeriesList(self):
        fipsList = ["26093"]
        downloader = Downloader(["BLS"], fipsList)
        expected_series_list = []
        for sridList in itertools.product(config["BLS_TABLE_NUMBER"],
                                          fipsList,
                                          config["BLS_DATA_TYPE"],
                                          config["BLS_SIZE"],
                                          config["BLS_OWNERSHIP"],
                                          config["BLS_NAICS_CODE_LIST"]):
            srid = ""
            for item in sridList:
                srid += item
            expected_series_list.append(srid)
        assert expected_series_list == downloader._getBLSSeriesList()

    def test_getBEAIncomePayload(self):
        fipsList = ["26093"]
        downloader = Downloader(["BEA"], fipsList)
        expected_series_list = []
        for payload in itertools.product(fipsList,
                                         config["BEA_LINE_CODE"],
                                         config["BEA_TABLE_NAME"],
                                         config["BEA_YEAR"]):
            expected_series_list.append(payload)
        assert expected_series_list == downloader._getBEAIncomePayload()

    def test_getBEAGDPPayload(self):
        fipsList = ["11460"]
        downloader = Downloader(["BEA-GDP"], fipsList)
        expected_series_list = []
        for payload in itertools.product(fipsList,
                                         config["BEA_GDP_COMPONENT"],
                                         config["BEA_GDP_INDUSTRY"],
                                         config["BEA_GDP_YEAR"]):
            expected_series_list.append(payload)
        assert expected_series_list == downloader._getBEAGDPPayload()
