import os
import requests
import itertools
from tqdm import tqdm
import pandas as pd
import json
import warnings
import time
import re
from socioFetcher.config import Config
from socioFetcher.geodataframe import GeoDataFrame
from socioFetcher.mapview import MapView


class Downloader:
    """
    A downloader to download data for Census Geography
     given configration from BLS, BEA, or Census.

    Attributes
    ----------
    dataset : List   
        List of dataset name, value must be
        must be one of BLS, BEA,BEAGDP, or ACS
    fipsList : List   
        List of FIPS code
    data : dict   
        dict to save downloaded data
    options : dict, optional
        Including years, Industries code, table
        name, subject, detail
    """

    def __init__(self, dataset, fipsList, config=Config()):
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

        Parameters
        ----------
            None

        Returns
        ----------
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

    def export(self, path, summarize=False, by="geography", saveformat="csv", orient="index", suffix=""):
        """
        Save downloaded data to specified path

        Parameters
        ----------
        path:str
            Abosolute path to a folder where files will be saved
        summarize:bolean, optional
            Save summarized data, default is False
        by:str
            Summarize option, one of geography and dataset
        saveformat:str
            Export format, "csv" or "json"
        orient:str
            Only apply to json export, define orient for json export
            visit https://pandas.pydata.org/pandas-docs/version/0.24.2/reference/api/pandas.DataFrame.to_json.html
        surffix:str
            Surffix after default name, used for differentiate versions of data

        Returns
        ----------
            None
        """
        if not os.path.exists(path):
            os.mkdir(path)
        if not summarize:
            for areaID, obj in self.data.items():
                areaName = self.config.Global.FIPS_CODE[areaID]
                for datasetName, geoDf in obj.items():
                    savePath = os.path.join(path, areaName)
                    os.makedirs(savePath, exist_ok=True)
                    if saveformat.lower() == "csv":
                        geoDf.DataFrame.to_csv(
                            os.path.join(
                                savePath, f"{datasetName}{suffix.strip()}.csv")
                        )
                    else:
                        geoDf.DataFrame.to_json(
                            os.path.join(
                                savePath, f"{datasetName}{suffix.strip()}.json"),
                            orient=orient
                        )
        else:
            summary = self.summarize(by=by)
            if by.lower() == "geography":
                for areaID, Df in summary.items():
                    areaName = self.config.Global.FIPS_CODE[areaID]
                    if saveformat.lower() == "csv":
                        Df.to_csv(
                            os.path.join(
                                path, f"{areaName}{suffix.strip()}.csv")
                        )
                    else:
                        Df.to_json(
                            os.path.join(
                                path, f"{areaName}{suffix.strip()}.json"),
                            orient=orient
                        )
            elif by.lower() == "dataset":
                for datasetName, Df in summary.items():
                    if saveformat.lower() == "csv":
                        Df.to_csv(
                            os.path.join(
                                path, f"{datasetName}{suffix.strip()}.csv")
                        )
                    else:
                        Df.to_json(
                            os.path.join(
                                path, f"{datasetName}{suffix.strip()}.json"),
                            orient=orient
                        )

    def summarize(self, by="geography"):
        """
        Process downloaded data and produce summrized table by
        either geography or dataset

        Parameters
        ------------
        by:str  
            On which summarize will based on, must be one of
            geography and dataset

        Returns
        ------------
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
        -----------
        dataset:str 
            The name of dataset to be mapped

        Returns
        -----------
        mapView:SocioFetcher.MapView
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
        """
        Generate choropleth data for mapping use in MapView

        Parameters
        ----------
        dataset:str
            The name of the dataset to be ploted in choropleth map

        Returns
        ----------
        choro_data:dict {attributeName=>{year=>{areaID=>value}}}
        """
        # self.data => choro_data for given dataset
        choro_data = {}
        for areaID, areaDict in tqdm(self.data.items(), desc="Getting Choro data"):
            areaDatasetDict = areaDict[dataset].DataFrame.to_dict(
                orient="dict")
            for attrID, attrdict in areaDatasetDict.items():
                if dataset.upper() == 'BLS':
                    blsAttrLookUp = {
                        **self.config.BLS.NAICS_CODE_LIST, **self.config.BLS.MEASURE_CODE}
                    attrName = blsAttrLookUp[attrID]
                elif dataset.upper() == 'ACS':
                    if attrID in self.config.ACS.SUBJECT_LIST.keys():
                        attrName = self.config.ACS.SUBJECT_LIST[attrID]
                    else:
                        attrName = self.config.ACS.DETAIL_LIST[attrID]
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

        Parameters
        ------------
        fipsList:list of str
            Requested FIPS code list
        outFields:list
            Fields included in the geojson response, default is ["GEOID"]
        geo : str
            default is "county", (Only support County)

        Returns
        -----------
        geojson:dict
            GeoJSON obj
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

        Parameters
        ----------
            None

        Returns
        ----------
        geoClassDict:dict
            key: FIPS:str,
            value: socioFetcher.GeoDataFrame
        """
        seriesList = self._getBLSSeriesList()
        n = 50  # Chunk size
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
        fipsLength = len(self.fipsList[0])
        p = re.compile(r"[A-Z]+\d{"+ str(fipsLength) +"}")
        for srsList in tqdm(seriesListChunk, desc="Download BLS data"):
            data = json.dumps({"seriesid": srsList,
                               "startyear": self.config.BLS.START_YEAR,
                               "endyear": self.config.BLS.END_YEAR,
                               "registrationkey": self.config.BLS.API_KEY,
                               "calculations": "true",
                               "annualaverage": self.config.BLS.ANNUAL_AVERAGE})
            r = s.post(
                'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                data=data)
            n_retry = 0
            while r.status_code != requests.codes.ok and n_retry < 10:
                warnings.warn(
                    f"Request server fail with error code {str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.post(
                    'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                    data=data)
                n_retry += 1
            json_data = r.json()
            for seriesResult in json_data["Results"]["series"]:
                m = p.match(seriesResult["seriesID"])
                areaCode = m.group()[-fipsLength:]
                geoClassDict[areaCode].load(seriesResult, fips=areaCode)
                # geoClassDict[areaCode].DataFrame = geoClassDict[areaCode].DataFrame.rename(
                #     self.config.BLS.MEASURE_CODE, axis=1)
        return geoClassDict

    def downloadBEAIncome(self):
        """
        Download BEA data given configuration from constructor.

        Parameters
        -----------
            None

        Returns
        -----------
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
            # sleep .6 second
            time.sleep(0.6)
            n_retry = 0
            while r.status_code != requests.codes.ok and n_retry < 10:
                warnings.warn(
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
                n_retry += 1
            json_data = r.json()
            areaCode = BEApaylaod[0]
            geoClassDict[areaCode].load(json_data, source="BEA")
        return geoClassDict

    def downloadBEAGDP(self):
        """
        Download BEAGDP data given configuration from constructor.

        Parameters
        ----------
            None

        Returns
        ----------
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
            "datasetname": "REGIONAL"
        }
        for BEApaylaod in tqdm(beaPayloadList, desc="Download GDP from BEA"):
            payload = {
                "GeoFips": BEApaylaod[0],
                "TableName": BEApaylaod[1],
                "LineCode": BEApaylaod[2],
                "Year": BEApaylaod[3]
            }
            s.params.update(payload)
            r = s.get("https://apps.bea.gov/api/data/")
            # sleep .6 second
            time.sleep(0.6)
            n_retry = 0
            while r.status_code != requests.codes.ok and n_retry < 10:
                print(f"Request fail when requesting {r.url}")
                warnings.warn(
                    f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                    ResourceWarning)
                time.sleep(10)
                r = s.get("https://apps.bea.gov/api/data/")
                n_retry += 1
            json_data = r.json()
            areaCode = BEApaylaod[0]
            GDPdataDict[BEApaylaod[0]].load(json_data, source="BEAGDP")

        return GDPdataDict

    def downloadACS(self):
        """
        Download ACS data given configuration from constructor.

        Parameters
        ----------
            None

        Returns
        -----------
        geoClassDict:dict
            key: FIPS:str,
            value: socioFetcher.GeoDataFrame
        """
        geoClassDict = {}
        for areaID in self.fipsList:
            name = self.config.Global.FIPS_CODE[areaID]
            geoClassDict[areaID] = GeoDataFrame(name, dataset="ACS")
        ACSPayload = self._getACSPayload()
        # Initialize session and default data
        s = requests.Session()
        s.params = {
            "key": self.config.ACS.API_KEY
        }
        for payload in tqdm(ACSPayload, desc="Download ACS Table"):
            for field in payload[-1]:
                fieldID = field["id"]
                year = payload[0]
                data = field["data"].lower()
                subcategory = field["availability"]["subcategory"]
                subject = "subject" if field["availability"]["subject"] else ""
                requestpayload = {
                    "get": fieldID,
                    "for": "county:"+payload[1],
                    "in": "state:"+payload[2]
                }
                s.params.update(requestpayload)
                r = s.get(
                    f"https://api.census.gov/data/{year}/{data}/{subcategory}/{subject}")
                n_retry = 0
                if r.status_code == 404:
                    
                    print(
                        f"Requesting acs {year} {data} fail. Response: 404. Dataset unavailable.")
                    continue
                while r.status_code != requests.codes.ok and n_retry < 10:
                    print(f"Request fail when requesting {r.url}")
                    warnings.warn(
                        f"Request server fail with error code ${str(r.status_code)}, sleep 10 sec",
                        ResourceWarning)
                    time.sleep(10)
                    r = s.get(
                        f"https://api.census.gov/data/{year}/{data}/{subcategory}/{subject}")
                    n_retry += 1
                json_data = r.json()
                areaCode = payload[2]+payload[1]
                geoClassDict[areaCode].load(
                    json_data, source="ACS", year=year)

        for key, _ in geoClassDict.items():
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
        # QCEW - State and County Employment and Wages(Quarterly Census of Employment & Wages)
        if "EN" in self.config.BLS.TABLE_NUMBER:
            for sridTup in itertools.product(self.config.BLS.EN_SEASONAL_ADJUST_CODE,
                                             self.fipsList,
                                             self.config.BLS.EN_DATA_TYPE,
                                             self.config.BLS.EN_SIZE,
                                             self.config.BLS.EN_OWNERSHIP,
                                             self.config.BLS.EN_NAICS_CODE_LIST.keys()):
                sridList = list(sridTup)
                if sridList[-1] == "10":
                    # if is Total, change ownership to all
                    sridList[-2] = "0"
                srid = "EN"
                for item in sridList:
                    srid += item
                seriesList.append(srid)
        # LAUS - Unemployment Data
        if "LA" in self.config.BLS.TABLE_NUMBER:
            for sridTup in itertools.product(self.config.BLS.LA_SEASONAL_ADJUST_CODE,
                                             self.fipsList,
                                             self.config.BLS.LA_MEASURE_CODE.keys()):
                sridList = list(sridTup)
                # Convert fipscode to area code
                sridList[1] = f"CN{sridList[1]}00000000"
                srid = "LA"
                for item in sridList:
                    srid += item
                seriesList.append(srid)
        # CES - Current Employment Statistics 
        if "SM" in self.config.BLS.TABLE_NUMBER:
            for sridTup in itertools.product(self.config.BLS.SM_SEASONAL_ADJUST_CODE,
                                             self.fipsList,
                                             self.config.BLS.SM_INDUSTRY_CODE_LIST.keys(),
                                             self.config.BLS.SM_DATA_TYPE.keys()):
                sridList = list(sridTup)
                srid = "SM" # dataset code
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
                                         self.config.BEA.GDP_TABLE_NAME,
                                         self.config.BEA.GDP_LINE_CODE,
                                         self.config.BEA.GDP_YEAR):
            BEApayloadList.append(payload)
        return BEApayloadList

    def _getACSPayload(self):
        """
        Helper function to Generate Series List form given parameter list
        """
        ACSPayloadList = []
        for yearGeoPayload in itertools.product(self.config.ACS.YEAR,
                                                list(set([x[2:]
                                                          for x in self.fipsList])),
                                                list(set([x[:2] for x in self.fipsList]))):
            # append subject item id to the end
            yearGeoPayloadList = list(yearGeoPayload)
            yearGeoPayloadList.append(self.config.ACS.FIELDS)
            ACSPayloadList.append(yearGeoPayloadList)
        return ACSPayloadList


if __name__ == "__main__":
    myConfig = Config()
    myConfig.ACS.API_KEY = "a1b79f5105b689bd9c4ed357de83130393b6dec7"
    myConfig.ACS.YEAR = ["2010", "2011", "2012",
                         "2013", "2014", "2015", "2016", "2017", "2018"]
    myConfig.ACS.FIELDS = [
        {
        "data": "acs",
        "id": "S0101_C01_001E",
        "desc": "Total Population",
        "availability": {
            "subcategory": "acs1",
            "subject": True
        }
    },
    {
        "data": "acs",
        "id": "S0102_C01_034E",
        "desc": "Less than high school graduate",
        "availability": {
            "subcategory": "acs5",
            "subject": True
        }
    }
    ]
    datasets = ["ACS"]
    fips = {"26093": "Livingston,MI"}
    dl = Downloader(datasets, list(fips.keys()), config=myConfig)
    dl.download()
