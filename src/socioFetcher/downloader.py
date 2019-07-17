import requests
import itertools
import pandas as pd
import json
import warnings
from socioFetcher.geodataframe import GeoDataFrame
from socioFetcher.config import config


class Downloader:
    """
        A downloader to download data for Census Geography
     given configration from BLS, BEA, or Census.

    Attributes:
        dataset:List    dataset name list for download use
        fipsList:List   FIPS list for download use
    """

    def __init__(self, dataset, fipsList, **kwargs):
        """
            The constructor for Downloader class

        Parameters:
           dataset:List   List of dataset name, value must be
                        must be one of BLS, BEA,BEA-GDP, or ACS
           fipsList:List   List of FIPS code
           data:dict    dict to save downloaded data 
           (optional)
           options:dict     Including years, Industries code, table
                        name, subject, detail
        """
        # value checking
        if type(dataset) != type([]) or len(dataset) < 1:
            raise TypeError(
                "dataset is not a valid list with more than one element")
        # Check the dataset name inside the allowed range
        elif not all([True if i in config.get("GLOBAL_ALLOWED_DATASET") else False for i in dataset]):
            raise ValueError(
                "value in dataset is not supported"
            )
        if type(fipsList) != type([]) or len(fipsList) < 1:
            raise TypeError(
                "fipsList is not a valid list with more than one element")
        # Check the length of FIPS code
        elif not all([True if len(i) == 5 else False for i in fipsList]):
            raise ValueError(
                "value in fipsList is not supported"
            )
        self.dataset = dataset
        self.fipsList = fipsList
        self.data = {fips: {} for fips in self.fipsList}
        self.config = config
        self.config.update(kwargs)

    def download(self):
        """
            Download data and save to self.data given configuration from
        constructor.

        Parameters:
            None

        Returns: 
            None
        """
        for dataset in self.dataset:
            if dataset.upper() == "BLS":
                res = self.downloadBLS()
            elif dataset.upper() == "BEA":
                res = self.downloadBEAIncome()
            elif dataset.upper() == "BEA-GDP":
                res = self.downloadBEAGDP()
            elif dataset.upper() == "ACS":
                res = self.downloadACS()
            for fips, geoDf in res.items():
                self.data[fips][dataset] = geoDf

    def downloadBLS(self):
        """
            Download BLS data given configuration from constructor.

        Parameters:
            None

        Returns: 
            geoClassDict:dict   
                key: FIPS:str,
                value: socioFetcher.GeoDataFrame
        """
        seriesList = self._getBLSSeriesList()
        n = 500
        seriesListChunk = [seriesList[i*n: (i+1)*n]
                           for i in range((len(seriesList)+n-1)//n)]
        # Creating counties class to hold class
        geoClassDict = {}
        for areaID in self.fipsList:
            name = self.config["GLOBAL_AREA_CODE"][areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="BLS")
        for srsList in seriesListChunk:
            headers = {'Content-type': 'application/json'}
            data = json.dumps(
                {"seriesid": srsList,
                 "startyear": self.config["BLS_START_YEAR"],
                 "endyear": self.config["BLS_END_YEAR"],
                 "registrationkey": self.config["BLS_API_KEY"],
                 "calculations": "true",
                 "annualaverage": "true"})
            r = requests.post(
                'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                data=data, headers=headers)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = requests.post(
                    'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                    data=data, headers=headers)
            json_data = r.json()
            for seriesResult in json_data["Results"]["series"]:
                areaCode = seriesResult["seriesID"][3:8]
                print("Loading Data for " +
                      self.config["GLOBAL_AREA_CODE"][areaCode])
                geoClassDict[areaCode].load(seriesResult)
        return geoClassDict

    def downloadBEAIncome(self):
        """
            Download BEA data given configuration from constructor.

        Parameters:
            None

        Returns: 
            geoClassDict:dict   
                key: FIPS:str,
                value: socioFetcher.GeoDataFrame
        """
        geoClassDict = {}
        for areaID in self.fipsList:
            name = self.config["GLOBAL_AREA_CODE"][areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="BEA")
        beaPayloadList = self._getBEAIncomePayload()
        for BEApaylaod in beaPayloadList:
            payload = {
                "UserID": self.config["BEA_API_KEY"],
                "Method": "GetData",
                "datasetname": "Regional",
                "GeoFips": BEApaylaod[0],
                "LineCode": BEApaylaod[1],
                "TableName": BEApaylaod[2],
                "Year": BEApaylaod[3]
            }

            r = requests.get("https://apps.bea.gov/api/data/",
                             params=payload)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = requests.get("https://apps.bea.gov/api/data/",
                                 params=payload)
            json_data = r.json()
            areaCode = BEApaylaod[0]
            print("Loading Data for " +
                  self.config["GLOBAL_AREA_CODE"][areaCode])
            geoClassDict[areaCode].load(json_data, source="BEA")
        return geoClassDict

    def downloadBEAGDP(self):
        """
            Download BEA-GDP data given configuration from constructor.

        Parameters:
            None

        Returns: 
            geoClassDict:dict   
                key: FIPS:str,
                value: socioFetcher.GeoDataFrame
        """
        GDPdata = GeoDataFrame("Region", dataset="BEA-GDP")
        beaPayloadList = self._getBEAGDPPayload()
        for BEApaylaod in beaPayloadList:
            payload = {
                "UserID": self.config["BEA_API_KEY"],
                "Method": "GetData",
                "datasetname": "REGIONALPRODUCT",
                "GeoFips": BEApaylaod[0],
                "component": BEApaylaod[1],
                "IndustryId": BEApaylaod[2],
                "Year": BEApaylaod[3]
            }

            r = requests.get("https://apps.bea.gov/api/data/",
                             params=payload)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = requests.get("https://apps.bea.gov/api/data/",
                                 params=payload)
            json_data = r.json()
            areaCode = BEApaylaod[0]
            print("Loading Data for " +
                  self.config["GLOBAL_AREA_CODE"][areaCode])
            GDPdata.load(json_data, source="BEA-GDP")
        return GDPdata.countyData

    def downloadACS(self):
        """
            Download ACS data given configuration from constructor.

        Parameters:
            None

        Returns: 
            geoClassDict:dict   
                key: FIPS:str,
                value: socioFetcher.GeoDataFrame
        """
        geoClassDict = {}
        detGeoClassDict = {}
        for areaID in self.fipsList:
            name = self.config["GLOBAL_AREA_CODE"][areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="ACS")
            detGeoClassDict[areaID] = GeoDataFrame(name, dataset="ACS")
        ACSPayload = self._getACSPayload()
        subjectPayload = ACSPayload["SUBJECT"]
        detailPayload = ACSPayload["DETAIL"]
        for sbjPay in subjectPayload:
            getSbjStr = ""
            for att in sbjPay[-1]:
                getSbjStr += att+","
            payload = {
                "key": self.config["CENSUS_API_KEY"],
                "get": getSbjStr[:-1],  # remove the last comma
                "for": "county:"+sbjPay[1],
                "in": "state:"+sbjPay[2]
            }

            r = requests.get(f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject",
                             params=payload)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = requests.get(f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject",
                                 params=payload)
            json_data = r.json()
            areaCode = sbjPay[1]
            print("Loading Data for " +
                  self.config["GLOBAL_AREA_CODE"][areaCode])
            geoClassDict[sbjPay[2]+sbjPay[1]].load(
                json_data, source="ACS", year=sbjPay[0])

        for detPay in detailPayload:
            getDetStr = ""
            for att in detPay[-1]:
                getDetStr += att+","
            payload = {
                "key": self.config["CENSUS_API_KEY"],
                "get": getDetStr[:-1],  # remove the last comma
                "for": "county:"+detPay[1],
                "in": "state:"+detPay[2]
            }
            r = requests.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1",
                             params=payload)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = requests.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1",
                                 params=payload)
            json_data = r.json()
            areaCode = detPay[1]
            print("Loading Data for " +
                  self.config["GLOBAL_AREA_CODE"][areaCode])
            detGeoClassDict[detPay[2]+detPay[1]].load(
                json_data, source="ACS", year=detPay[0])
        # merge two dicts
        for key, _ in geoClassDict.items():
            geoClassDict[key].countyData = pd.concat(
                [geoClassDict[key].countyData,
                 detGeoClassDict[key].countyData],
                axis=1, sort=True)

        return geoClassDict

    def _getBLSSeriesList(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        seriesList = []
        for sridList in itertools.product(self.config["BLS_TABLE_NUMBER"],
                                          self.fipsList,
                                          self.config["BLS_DATA_TYPE"],
                                          self.config["BLS_SIZE"],
                                          self.config["BLS_OWNERSHIP"],
                                          self.config["BLS_NAICS_CODE_LIST"]):
            srid = ""
            for item in sridList:
                srid += item
            seriesList.append(srid)
        return seriesList

    def _getBEAIncomePayload(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        BEApayloadList = []
        for payload in itertools.product(self.fipsList,
                                         self.config["BEA_LINE_CODE"],
                                         self.config["BEA_TABLE_NAME"],
                                         self.config["BEA_YEAR"]):
            BEApayloadList.append(payload)
        return BEApayloadList

    def _getBEAGDPPayload(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        BEApayloadList = []
        for payload in itertools.product(self.fipsList,
                                         self.config["BEA_GDP_COMPONENT"],
                                         self.config["BEA_GDP_INDUSTRY"],
                                         self.config["BEA_GDP_YEAR"]):
            BEApayloadList.append(payload)
        return BEApayloadList

    def _getACSPayload(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        ACSPayloadDict = {
            "SUBJECT": [],
            "DETAIL": []
        }
        for payload in itertools.product(self.config["CENSUS_YEAR"],
                                         [x[2:] for x in self.fipsList],
                                         [x[:2] for x in self.fipsList]):
            # append subject item id to the end
            subjectList = list(payload)
            detailList = list(payload)
            subjectList.append(self.config["CENSUS_SUBJECT_LIST"].keys())
            detailList.append(self.config["CENSUS_DETAIL_LIST"].keys())
            ACSPayloadDict["SUBJECT"].append(subjectList)
            ACSPayloadDict["DETAIL"].append(detailList)
        return ACSPayloadDict
