import pytest
from socioFetcher.downloader import Downloader


class TestDownload:
    @pytest.mark.parametrize('dataset, fipsList', [
        (['BEA', 'BLS', 'ACS'], ["26093"]),
        (['BEA', 'BLS'], ["26093"]),
        (['BEA'], ["26093"]),
        (['BEAGDP'], ["11460"])
    ])
    def test_download(self, dataset, fipsList):
        print(dataset)
        downloader = Downloader(dataset, fipsList)
        downloader.download()
        assert list(downloader.data.keys()) == fipsList
