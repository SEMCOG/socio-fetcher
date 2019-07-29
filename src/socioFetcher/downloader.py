import os
import requests
import itertools
from tqdm import tqdm
import pandas as pd
import json
import warnings
import time
from socioFetcher.config import Config
from socioFetcher.geodataframe import GeoDataFrame
from socioFetcher.mapview import MapView


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
        elif not all([True if i.upper() in config.Global.ALLOWED_DATASET else False for i in dataset]):
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

    def mapping(self, dataset=None):
        """
            Mapping the selected downloaded data in form of Interactive map
        Parameters
            dataset:str     The name of dataset to be mapped

        Returns:
            mapView:SocioFetcher.MapView object
        """
        geodata = self.get_geojson_from_TIGER(
            self.fipsList, outFields=["GEOID"], geo="county")
        choro_data = self.get_choro_data(dataset)
        mapView = MapView(
            dataset,
            geodata,
            choro_data,
            {idx: self.config.Global.FIPS_CODE[idx] for idx in self.fipsList}
        )
        return mapView

    def get_choro_data(self, dataset):
        """)
            Generate choropleth data for mapping use in MapView

        Parameters:
            dataset:str     The name of the dataset to be ploted in choropleth map

        Returns:
            choro_data:dict {attributeName=>{year=>{areaID=>value}}}
        """
        # self.data => choro_data for given dataset
        choro_data = {}
        for areaID, areaDict in tqdm(self.data.items(), desc="Getting Choro data"):
            areaDatasetDict = areaDict[dataset].DataFrame.to_dict(
                orient="dict")
            for attrID, attrdict in areaDatasetDict.items():
                if dataset.upper() == 'BLS':
                    attrName = self.config.BLS.NAICS_CODE_LIST[attrID]
                elif dataset.upper() == 'ACS':
                    if attrID in self.config.Census.SUBJECT_LIST.keys():
                        attrName = self.config.Census.SUBJECT_LIST[attrID]
                    else:
                        attrName = self.config.Census.DETAIL_LIST[attrID]
                else:
                    attrName = attrID
                if not attrName in choro_data.keys():
                    choro_data[attrName] = {}
                for year, data in attrdict.items():
                    if not year in choro_data[attrName].keys():
                        choro_data[attrName][year] = {}
                    choro_data[attrName][year][areaID] = data
        return choro_data

    def get_geojson_from_TIGER(self, fipsList, outFields=["GEOID"], geo="county"):
        """
            Get geojson from Census TIGER REST API(Only support county level for now)
        Parameters:
            fipsList:list   Requested FIPS code list
            outFields:list  Fields included in the geojson response
            geo          Only support County

        Returns:
            geojson:dict  GeoJSON obj
        """
        if geo.lower() == 'county':
            where = ""
            for i, fips in enumerate(fipsList):
                where += f"(STATE='{fips[:2]}' AND COUNTY='{fips[2:]}')"
                if i != len(fipsList)-1:
                    where += " OR "
        else:
            # other geo, census tract, block groups ...
            pass
        params = {
            "where": where,
            "outFields": ",".join(outFields),
            "f": "geojson", "text": "",
            "objectIds": "", "time": "",
            "geometry": "", "geometryType": "esriGeometryEnvelope",
            "inSR": "", "spatialRel": "esriSpatialRelIntersects",
            "relationParam": "", "returnGeometry": True,
            "returnTrueCurves": False, "maxAllowableOffset": "",
            "geometryPrecision": "", "outSR": "", "returnIdsOnly": False,
            "returnCountOnly": False, "orderByFields": "",
            "groupByFieldsForStatistics": "", "outStatistics": "",
            "returnZ": False, "returnM": False, "gdbVersion": "",
            "returnDistinctValues": False, "resultOffset": "",
            "resultRecordCount": "", "queryByDistance": "",
            "returnExtentsOnly": False, "datumTransformation": "",
            "parameterValues": "", "rangeValues": ""
        }
        r = requests.get(
            "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query",
            params=params
        )
        while r.status_code != requests.codes.ok:
            warnings.warn(
                f"Request server fail when getting geojson from TIGER with error code {str(r.status_code)}, sleep 10 sec",
                ResourceWarning)
            time.sleep(10)
            r = requests.get(
                "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query",
                params=params
            )
        geojson = r.json()
        # add id
        for i, feature in enumerate(geojson["features"]):
            geojson["features"][i]["id"] = geojson["features"][i]["properties"]["GEOID"]
        return geojson

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
        for srsList in tqdm(seriesListChunk, desc="Download BLS data"):
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
                    f"Request server fail with error code {str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.post(
                    'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                    data=data, headers=headers)
            json_data = r.json()
            for seriesResult in json_data["Results"]["series"]:
                areaCode = seriesResult["seriesID"][3:8]
                # print("Loading Data for " +
                #       self.config.Global.FIPS_CODE[areaCode])
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
        for BEApaylaod in tqdm(beaPayloadList, desc="Download BEA"):
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
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
            json_data = r.json()
            areaCode = BEApaylaod[0]
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
        for BEApaylaod in tqdm(beaPayloadList, desc="Download GDP from BEA"):
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
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
            json_data = r.json()
            areaCode = BEApaylaod[0]
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
        for sbjPay in tqdm(subjectPayload, desc="Download ACS Subject Table"):
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
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get(
                    f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject")
            json_data = r.json()
            areaCode = sbjPay[2]+sbjPay[1]
            geoClassDict[areaCode].load(
                json_data, source="ACS", year=sbjPay[0])

        for detPay in tqdm(detailPayload, desc="Download ACS Detail Table"):
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
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1")
            json_data = r.json()
            areaCode = detPay[2]+detPay[1]
            detGeoClassDict[detPay[2]+detPay[1]].load(
                json_data, source="ACS", year=detPay[0])
        # merge two dicts
        for key, _ in geoClassDict.items():
            geoClassDict[key].DataFrame = pd.concat(
                [geoClassDict[key].DataFrame,
                 detGeoClassDict[key].DataFrame],
                axis=1, sort=True)
            if "state" in geoClassDict[key].DataFrame.columns:
                del geoClassDict[key].DataFrame["state"]
            if "county" in geoClassDict[key].DataFrame.columns:
                del geoClassDict[key].DataFrame["county"]

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
                                          self.config.BLS.NAICS_CODE_LIST.keys()):
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


# downloader = Downloader(['BEA', 'BLS', 'ACS'], ["26161", "26163"])
# downloader.download()
# downloader.get_geojson_from_TIGER(["26161", "26163"])
