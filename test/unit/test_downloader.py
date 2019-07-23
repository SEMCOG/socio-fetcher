import pytest
import os
import itertools
from socioFetcher.downloader import Downloader
from socioFetcher.config import Config
from socioFetcher.geodataframe import GeoDataFrame


class TestDownloader:
    @pytest.mark.parametrize('dataset, fipsList', [
        (['BEA', 'BLS', 'ACS'], ["26093"]),
        (['BEA', 'BLS'], ["26093"]),
        (['BEA'], ["26093"]),
        (['BEAGDP'], ["11460"])
    ])
    def test_init_dataset(self, dataset, fipsList):
        downloader = Downloader(dataset, fipsList)
        assert downloader.dataset == dataset
        assert downloader.fipsList == fipsList
        assert downloader.data == {fips: {} for fips in fipsList}
        assert isinstance(downloader.config, Config)

    def test_init_dataset_get_raise(self):
        with pytest.raises(TypeError):
            Downloader([], ["26093"])
        with pytest.raises(TypeError):
            Downloader("BEA", ["26093"])
        with pytest.raises(ValueError):
            Downloader(["INVALID"], ["26093"])
        with pytest.raises(ValueError):
            Downloader(["BEA", "BEAGDP"], ["11460"])

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
        config = Config()
        for sridList in itertools.product(config.BLS.TABLE_NUMBER,
                                          fipsList,
                                          config.BLS.DATA_TYPE,
                                          config.BLS.SIZE,
                                          config.BLS.OWNERSHIP,
                                          config.BLS.NAICS_CODE_LIST):
            srid = ""
            for item in sridList:
                srid += item
            expected_series_list.append(srid)
        assert expected_series_list == downloader._getBLSSeriesList()

    def test_getBEAIncomePayload(self):
        fipsList = ["26093"]
        downloader = Downloader(["BEA"], fipsList)
        expected_series_list = []
        config = Config()
        for payload in itertools.product(fipsList,
                                         config.BEA.LINE_CODE,
                                         config.BEA.TABLE_NAME,
                                         config.BEA.YEAR):
            expected_series_list.append(payload)
        assert expected_series_list == downloader._getBEAIncomePayload()

    def test_getBEAGDPPayload(self):
        fipsList = ["11460"]
        downloader = Downloader(["BEAGDP"], fipsList)
        expected_series_list = []
        config = Config()
        for payload in itertools.product(fipsList,
                                         config.BEA.GDP_COMPONENT,
                                         config.BEA.GDP_INDUSTRY,
                                         config.BEA.GDP_YEAR):
            expected_series_list.append(payload)
        assert expected_series_list == downloader._getBEAGDPPayload()

    def test_downloadBLS(self):
        fipsList = ["26093"]
        downloader = Downloader(["BLS"], fipsList)
        downloader.download()
        assert downloader.data
        assert isinstance(downloader.data["26093"]["BLS"], GeoDataFrame)

    def test_downloadBEA(self):
        fipsList = ["26093"]
        downloader = Downloader(["BEA"], fipsList)
        downloader.download()
        assert downloader.data
        assert isinstance(downloader.data["26093"]["BEA"], GeoDataFrame)

    def test_downloadBEAGDP(self):
        fipsList = ["11460"]
        downloader = Downloader(["BEAGDP"], fipsList)
        downloader.download()
        assert downloader.data
        assert isinstance(downloader.data["11460"]["BEAGDP"], GeoDataFrame)

    def test_downloadACS(self):
        fipsList = ["26093"]
        downloader = Downloader(["ACS"], fipsList)
        downloader.download()
        assert downloader.data
        assert isinstance(downloader.data["26093"]["ACS"], GeoDataFrame)

    @pytest.mark.parametrize('dataset, fipsList', [
        (['BEA', 'BLS', 'ACS'], ["26093"]),
        (['BEA', 'BLS'], ["26093"]),
        (['BEA'], ["26093"]),
        (['BEAGDP'], ["11460"])
    ])
    def test_download(self, dataset, fipsList):
        downloader = Downloader(dataset, fipsList)
        downloader.download()
        data = downloader.data
        assert list(data.keys()) == fipsList
        assert list(data[fipsList[0]].keys()) == dataset

    @pytest.mark.parametrize('summarize, by', [
        (False, "geography"),
        (True, "geography"),
        (False, "dataset"),
        (True, "dataset")
    ])
    def test_export(self, summarize, by, tmpdir):
        downloader = Downloader(['BEA', 'BLS', 'ACS'], ["26161", "26163"])
        downloader.download()
        downloader.export(tmpdir, summarize=summarize, by=by)
        assert 1
