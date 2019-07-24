import os
import requests
import itertools
import pandas as pd
import json
import warnings
from socioFetcher.geodataframe import GeoDataFrame
from socioFetcher.config import Config


class Downloader:
    """
        A downloader to download data for Census Geography
     given configration from BLS, BEA, or Census.

    Attributes:
        dataset:List    dataset name list for download use
        fipsList:List   FIPS list for download use
    """

    def __init__(self, dataset, fipsList, config=Config()):
        """
            The constructor for Downloader class

        Parameters:
           dataset:List   List of dataset name, value must be
                        must be one of BLS, BEA,BEAGDP, or ACS
           fipsList:List   List of FIPS code
           data:dict    dict to save downloaded data 
           (optional)
           options:dict     Including years, Industries code, table
                        name, subject, detail
        """
        # value checking
        if config and not isinstance(config, Config):
            raise TypeError(
                "Config must be in Config object"
            )
        if type(dataset) != type([]) or len(dataset) < 1:
            raise TypeError(
                "dataset is not a valid list with more than one element")
        # Check the dataset name inside the allowed range
        elif not all([True if i in config.Global.ALLOWED_DATASET else False for i in dataset]):
            raise ValueError(
                "value in dataset is not supported"
            )
        elif len(dataset) > 1 and any([True if i.upper() == "BEAGDP" else False for i in dataset]):
            raise ValueError(
                "BEAGDP only apply for metropolitan area, dataset cannot include both BEAGDP and other dataset type"
            )

        if type(fipsList) != type([]) or len(fipsList) < 1:
            raise TypeError(
                "fipsList is not a valid list with more than one element")
        # Check the validity of FIPS code
        elif not all([True if i in config.Global.FIPS_CODE.keys() else False for i in fipsList]):
            raise ValueError(
                "value in fipsList is not supported"
            )

        self.dataset = dataset
        self.fipsList = fipsList
        self.data = {fips: {} for fips in self.fipsList}
        self.config = config

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
            elif dataset.upper() == "BEAGDP":
                res = self.downloadBEAGDP()
            elif dataset.upper() == "ACS":
                res = self.downloadACS()
            for fips, geoDf in res.items():
                self.data[fips][dataset] = geoDf

    def export(self, path, summarize=False, by="geography"):
        """
            Save downloaded data to specified path

        Parameters:
            path:str    Abosolute path to a folder where files will be saved
            (optional)
            summarize:bolean    Save summarized data, default is False
            by:str      Summarize option, one of geography and dataset

        Returns: 
            None
        """
        if not summarize:
            for areaID, obj in self.data.items():
                areaName = self.config.Global.FIPS_CODE[areaID]
                for datasetName, geoDf in obj.items():
                    savePath = os.path.join(path, areaName)
                    os.makedirs(savePath, exist_ok=True)
                    geoDf.DataFrame.to_csv(
                        os.path.join(savePath, f"{datasetName}.csv")
                    )
        else:
            summary = self.summarize(by=by)
            if by.lower() == "geography":
                for areaID, Df in summary.items():
                    areaName = self.config.Global.FIPS_CODE[areaID]
                    Df.to_csv(
                        os.path.join(path, f"{areaName}.csv")
                    )
            elif by.lower() == "dataset":
                for datasetName, Df in summary.items():
                    Df.to_csv(
                        os.path.join(path, f"{datasetName}.csv")
                    )

    def summarize(self, by="geography"):
        """
            Process downloaded data and produce summrized table by
        either geography or dataset 

        Parameters:
            by:str  On which summarize will based on, must be one of 
                    geography and dataset

        Returns: 
            tableDict:dict  
                    key: Name of Geography or Name of dataset
                    value: pandas.DataFrame
        """
        if by.lower() == "geography":
            areaTableDict = {}
            for areaID, obj in self.data.items():
                areaTable = pd.DataFrame()
                for datasetName, geoDf in obj.items():
                    localTable = geoDf.DataFrame
                    areaTable = pd.concat([areaTable, localTable],
                                          axis=1, sort=True)
                areaTableDict[areaID] = areaTable
            return areaTableDict
        elif by.lower() == "dataset":
            datasetTableDict = {}
            for datasetName in self.dataset:
                datasetTable = pd.DataFrame()
                for areaID, obj in self.data.items():
                    areaName = self.config.Global.FIPS_CODE[areaID]
                    localTable = obj[datasetName].DataFrame
                    localTable = localTable.rename(lambda x: f"{areaName} {x}",
                                                   axis="columns")
                    datasetTable = pd.concat([datasetTable, localTable],
                                             axis=1, sort=True)
                datasetTableDict[datasetName] = datasetTable
            return datasetTableDict

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
            name = self.config.Global.FIPS_CODE[areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="BLS")
        # Initialize session and default data
        s = requests.Session()
        s.headers = {'Content-type': 'application/json'}
        for srsList in seriesListChunk:
            data = json.dumps(
                {"seriesid": srsList,
                 "startyear": self.config.BLS.START_YEAR,
                 "endyear": self.config.BLS.END_YEAR,
                 "registrationkey": self.config.BLS.API_KEY,
                 "calculations": "true",
                 "annualaverage": "true"})
            r = s.post(
                'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                data=data)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code {str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.post(
                    'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                    data=data, headers=headers)
            json_data = r.json()
            for seriesResult in json_data["Results"]["series"]:
                areaCode = seriesResult["seriesID"][3:8]
                print("Loading Data for " +
                      self.config.Global.FIPS_CODE[areaCode])
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
            name = self.config.Global.FIPS_CODE[areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="BEA")
        beaPayloadList = self._getBEAIncomePayload()
        # Initialize session and default data
        s = requests.Session()
        s.params = {
            "UserID": self.config.BEA.API_KEY,
            "Method": "GetData",
            "datasetname": "Regional"
        }
        for BEApaylaod in beaPayloadList:
            payload = {
                "GeoFips": BEApaylaod[0],
                "LineCode": BEApaylaod[1],
                "TableName": BEApaylaod[2],
                "Year": BEApaylaod[3]
            }
            s.params.update(payload)
            r = s.get("https://apps.bea.gov/api/data/")
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
            json_data = r.json()
            areaCode = BEApaylaod[0]
            print("Loading Data for " +
                  self.config.Global.FIPS_CODE[areaCode])
            geoClassDict[areaCode].load(json_data, source="BEA")
        return geoClassDict

    def downloadBEAGDP(self):
        """
            Download BEAGDP data given configuration from constructor.

        Parameters:
            None

        Returns: 
            geoClassDict:dict   
                key: FIPS:str,
                value: socioFetcher.GeoDataFrame
        """
        GDPdataDict = {}
        for areaID in self.fipsList:
            name = self.config.Global.FIPS_CODE[areaID]
            GDPdataDict[areaID] = GeoDataFrame(name, dataset="BEAGDP")
        beaPayloadList = self._getBEAGDPPayload()
        # Initialize session and default data
        s = requests.Session()
        s.params = {
            "UserID": self.config.BEA.API_KEY,
            "Method": "GetData",
            "datasetname": "REGIONALPRODUCT"
        }
        for BEApaylaod in beaPayloadList:
            payload = {
                "GeoFips": BEApaylaod[0],
                "component": BEApaylaod[1],
                "IndustryId": BEApaylaod[2],
                "Year": BEApaylaod[3]
            }
            s.params.update(payload)
            r = s.get("https://apps.bea.gov/api/data/")
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
            json_data = r.json()
            areaCode = BEApaylaod[0]
            print("Loading Data for " +
                  self.config.Global.FIPS_CODE[areaCode])
            GDPdataDict[BEApaylaod[0]].load(json_data, source="BEAGDP")

        return GDPdataDict

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
            name = self.config.Global.FIPS_CODE[areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="ACS")
            detGeoClassDict[areaID] = GeoDataFrame(name, dataset="ACS")
        ACSPayload = self._getACSPayload()
        subjectPayload = ACSPayload["SUBJECT"]
        detailPayload = ACSPayload["DETAIL"]
        # Initialize session and default data
        s = requests.Session()
        s.params = {
            "key": self.config.Census.API_KEY
        }
        for sbjPay in subjectPayload:
            getSbjStr = ""
            for att in sbjPay[-1]:
                getSbjStr += att+","
            payload = {
                "get": getSbjStr[:-1],  # remove the last comma
                "for": "county:"+sbjPay[1],
                "in": "state:"+sbjPay[2]
            }
            s.params.update(payload)
            r = s.get(
                f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject")
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get(
                    f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject")
            json_data = r.json()
            areaCode = sbjPay[2]+sbjPay[1]
            print("Loading Data for " +
                  self.config.Global.FIPS_CODE[areaCode])
            geoClassDict[areaCode].load(
                json_data, source="ACS", year=sbjPay[0])

        for detPay in detailPayload:
            getDetStr = ""
            for att in detPay[-1]:
                getDetStr += att+","
            payload = {
                "get": getDetStr[:-1],  # remove the last comma
                "for": "county:"+detPay[1],
                "in": "state:"+detPay[2]
            }
            r = s.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1",
                      params=payload)
            while r.status_code != requests.codes.ok:
                warnings.warn(
                    f"Request server fail with error code ${str(p.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1")
            json_data = r.json()
            areaCode = detPay[2]+detPay[1]
            print("Loading Data for " +
                  self.config.Global.FIPS_CODE[areaCode])
            detGeoClassDict[detPay[2]+detPay[1]].load(
                json_data, source="ACS", year=detPay[0])
        # merge two dicts
        for key, _ in geoClassDict.items():
            geoClassDict[key].DataFrame = pd.concat(
                [geoClassDict[key].DataFrame,
                 detGeoClassDict[key].DataFrame],
                axis=1, sort=True)

        return geoClassDict

    def _getBLSSeriesList(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        seriesList = []
        for sridList in itertools.product(self.config.BLS.TABLE_NUMBER,
                                          self.fipsList,
                                          self.config.BLS.DATA_TYPE,
                                          self.config.BLS.SIZE,
                                          self.config.BLS.OWNERSHIP,
                                          self.config.BLS.NAICS_CODE_LIST):
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
                                         self.config.BEA.LINE_CODE,
                                         self.config.BEA.TABLE_NAME,
                                         self.config.BEA.YEAR):
            BEApayloadList.append(payload)
        return BEApayloadList

    def _getBEAGDPPayload(self):
        """
            Helper function to Generate Series List form given parameter list
        """
        BEApayloadList = []
        for payload in itertools.product(self.fipsList,
                                         self.config.BEA.GDP_COMPONENT,
                                         self.config.BEA.GDP_INDUSTRY,
                                         self.config.BEA.GDP_YEAR):
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
        for payload in itertools.product(self.config.Census.YEAR,
                                         list(set([x[2:]
                                                   for x in self.fipsList])),
                                         list(set([x[:2] for x in self.fipsList]))):
            # append subject item id to the end
            subjectList = list(payload)
            detailList = list(payload)
            subjectList.append(self.config.Census.SUBJECT_LIST.keys())
            detailList.append(self.config.Census.DETAIL_LIST.keys())
            ACSPayloadDict["SUBJECT"].append(subjectList)
            ACSPayloadDict["DETAIL"].append(detailList)
        return ACSPayloadDict

