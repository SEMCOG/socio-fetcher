"""Download data"""
import requests
import itertools
import pandas as pd
import json
import time

from utils.config import *
from utils.county import CountyDataFrame


def _getBLSSeriesList():
    """Generate Series List form given parameter list"""
    # Series ID format:
    # TABLE_ID + AREA_CODE + BLS_DATA_TYPE
    # + BLS_SIZE + BLS_OWNERSHIP + NAICS_CODE
    seriesList = []
    for sridList in itertools.product(BLS_TABLE_NUMBER,
                                      BLS_AREA_CODE.keys(),
                                      BLS_DATA_TYPE,
                                      BLS_SIZE,
                                      BLS_OWNERSHIP,
                                      NAICS_CODE_LIST):
        srid = ""
        for item in sridList:
            srid += item
        seriesList.append(srid)
    return seriesList


def BLSdownload():
    seriesList = _getBLSSeriesList()
    n = 500
    seriesListChunk = [seriesList[i*n: (i+1)*n]
                       for i in range((len(seriesList)+n-1)//n)]
    # Creating counties class to hold class
    countyClassDict = {}
    for areaID, name in BLS_AREA_CODE.items():
        countyClassDict[areaID] = CountyDataFrame(name, acceptData="BLS")
    for srsList in seriesListChunk:
        headers = {'Content-type': 'application/json'}
        data = json.dumps(
            {"seriesid": srsList,
             "startyear": BLS_START_YEAR,
             "endyear": BLS_END_YEAR,
             "registrationkey": BLS_API_KEY,
             "calculations": "true",
             "annualaverage": "true"})
        p = requests.post(
            'https://api.bls.gov/publicAPI/v2/timeseries/data/',
            data=data, headers=headers)
        if p.status_code != requests.codes.ok:
            print("Request fail-- " + str(p.status_code))
            print("Wait 10 secs...")
            time.sleep(10)
            p = requests.post(
                'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                data=data, headers=headers)
        json_data = p.json()
        for seriesResult in json_data["Results"]["series"]:
            areaCode = seriesResult["seriesID"][3:8]
            print("Loading Data for "+BLS_AREA_CODE[areaCode])
            countyClassDict[areaCode].load(seriesResult)
    return countyClassDict


def _getBEAIncomePayload():
    """Generate Series List form given parameter list
    {"Parameter":[
        {"ParameterName":
        "GeoFips","ParameterDataType":"string",
            "ParameterDescription":
            "Comma-delimited list of 5-character geographic codes;
            COUNTY for all counties, STATE for all states,
            MSA for all MSAs, MIC for all Micropolitan Areas,
            PORT for all state metro/nonmetro portions,
            DIV for all Metropolitan Divisions,
            CSA for all Combined Statistical Areas,
            state post office abbreviation for all counties in
            one state (e.g. NY)",
            "ParameterIsRequiredFlag":"1",
            "MultipleAcceptedFlag":"1"},
        {"ParameterName":"LineCode","ParameterDataType":"integer",
            "ParameterDescription":"Line code for a statistic or
            industry","ParameterIsRequiredFlag":"1","MultipleAcceptedFlag":
            "0"},
        {"ParameterName":"TableName","ParameterDataType":"string",
            "ParameterDescription":"Regional income or product table
            to retrieve","ParameterIsRequiredFlag":"1",
            "ParameterDefaultValue":"","MultipleAcceptedFlag":"0"},
        {"ParameterName":"Year","ParameterDataType":"string",
            "ParameterDescription":"Comma-delimted list of years;
            LAST5 for latest 5 years; LAST10 for latest 10 years;
            ALL for all years","ParameterIsRequiredFlag":"0",
            "ParameterDefaultValue":"LAST5","MultipleAcceptedFlag":"1"}]}}}
    """

    BEApayloadList = []
    for payload in itertools.product(BEA_GEO_FIPS.keys(),
                                     BEA_LINE_CODE,
                                     BEA_TABLE_NAME,
                                     BEA_YEAR):
        BEApayloadList.append(payload)
    return BEApayloadList


def BEAIncomeDownload():
    countyClassDict = {}
    for areaID, name in BEA_GEO_FIPS.items():
        countyClassDict[areaID] = CountyDataFrame(name, acceptData="BEA")
    beaPayloadList = _getBEAIncomePayload()
    for BEApaylaod in beaPayloadList:
        payload = {
            "UserID": BEA_API_KEY,
            "Method": "GetData",
            "datasetname": "Regional",
            "GeoFips": BEApaylaod[0],
            "LineCode": BEApaylaod[1],
            "TableName": BEApaylaod[2],
            "Year": BEApaylaod[3]
        }

        r = requests.get("https://apps.bea.gov/api/data/",
                         params=payload)
        if r.status_code != requests.codes.ok:
            print("Request fail-- " + str(r.status_code))
            print("Wait 10 secs...")
            time.sleep(10)
            r = requests.get("https://apps.bea.gov/api/data/",
                             params=payload)
        json_data = r.json()
        areaCode = BEApaylaod[0]
        print("Loading Data for "+BEA_GEO_FIPS[areaCode])
        countyClassDict[areaCode].load(json_data, source="BEA")
    return countyClassDict


def _getBEAGDPPayload():
    BEApayloadList = []
    for payload in itertools.product(BEA_GDP_METRO_CODE.keys(),
                                     BEA_GDP_COMPONENT,
                                     BEA_GDP_INDUSTRY,
                                     BEA_GDP_YEAR):
        BEApayloadList.append(payload)
    return BEApayloadList


def BEAGDPDownload():
    GDPdata = CountyDataFrame("Region", acceptData="BEA-GDP")
    beaPayloadList = _getBEAGDPPayload()
    for BEApaylaod in beaPayloadList:
        payload = {
            "UserID": BEA_API_KEY,
            "Method": "GetData",
            "datasetname": "REGIONALPRODUCT",
            "GeoFips": BEApaylaod[0],
            "component": BEApaylaod[1],
            "IndustryId": BEApaylaod[2],
            "Year": BEApaylaod[3]
        }

        r = requests.get("https://apps.bea.gov/api/data/",
                         params=payload)
        if r.status_code != requests.codes.ok:
            print("Request fail-- " + str(r.status_code))
            print("Wait 10 secs...")
            time.sleep(10)
            r = requests.get("https://apps.bea.gov/api/data/",
                             params=payload)
        json_data = r.json()
        areaCode = BEApaylaod[0]
        print("Loading Data for "+BEA_GDP_METRO_CODE[areaCode])
        GDPdata.load(json_data, source="BEA-GDP")
    return GDPdata.countyData


def _getACSPayload():
    ACSPayloadDict = {
        "SUBJECT": [],
        "DETAIL": []
    }
    for payload in itertools.product(CENSUS_YEAR,
                                     CENSUS_COUNTY_CODE.keys(),
                                     CENSUS_STATE_CODE):
        # append subject item id to the end
        subjectList = list(payload)
        detailList = list(payload)
        subjectList.append(CENSUS_SUBJECT_LIST.keys())
        detailList.append(CENSUS_DETAIL_LIST.keys())
        ACSPayloadDict["SUBJECT"].append(subjectList)
        ACSPayloadDict["DETAIL"].append(detailList)
    return ACSPayloadDict


def ACSDownload():
    countyClassDict = {}
    for areaID, name in CENSUS_COUNTY_CODE.items():
        countyClassDict[CENSUS_STATE_CODE[0] +
                        areaID] = CountyDataFrame(name, acceptData="ACS")
    ACSPayload = _getACSPayload()
    subjectPayload = ACSPayload["SUBJECT"]
    detailPayload = ACSPayload["DETAIL"]
    for sbjPay in subjectPayload:
        getSbjStr = ""
        for att in sbjPay[-1]:
            getSbjStr += att+","
        payload = {
            "key": CENSUS_API_KEY,
            "get": getSbjStr[:-1],  # remove the last comma
            "for": "county:"+sbjPay[1],
            "in": "state:"+sbjPay[2]
        }

        r = requests.get(f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject",
                         params=payload)
        while r.status_code != requests.codes.ok:
            print("Request fail-- " + str(r.status_code))
            print("Wait 10 secs...")
            time.sleep(10)
            r = requests.get(f"https://api.census.gov/data/{sbjPay[0]}/acs/acs5/subject",
                             params=payload)
        json_data = r.json()
        areaCode = sbjPay[1]
        print("Loading Data for "+CENSUS_COUNTY_CODE[areaCode])
        countyClassDict[sbjPay[2]+sbjPay[1]].load(
            json_data, source="ACS", year=sbjPay[0])
    detCountyClassDict = {}
    for areaID, name in CENSUS_COUNTY_CODE.items():
        detCountyClassDict[CENSUS_STATE_CODE[0] +
                           areaID] = CountyDataFrame(name, acceptData="ACS")
    for detPay in detailPayload:
        getDetStr = ""
        for att in detPay[-1]:
            getDetStr += att+","
        payload = {
            "key": CENSUS_API_KEY,
            "get": getDetStr[:-1],  # remove the last comma
            "for": "county:"+detPay[1],
            "in": "state:"+detPay[2]
        }

        r = requests.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1",
                         params=payload)
        while r.status_code != requests.codes.ok:
            print("Request fail-- " + str(r.status_code))
            print("Wait 10 secs...")
            time.sleep(10)
            r = requests.get(f"https://api.census.gov/data/{detPay[0]}/acs/acs1",
                             params=payload)
        json_data = r.json()
        areaCode = detPay[1]
        print("Loading Data for "+CENSUS_COUNTY_CODE[areaCode])
        detCountyClassDict[detPay[2]+detPay[1]].load(
            json_data, source="ACS", year=detPay[0])
    # merge two dicts
    for key, _ in countyClassDict.items():
        countyClassDict[key].countyData = pd.concat(
            [countyClassDict[key].countyData,
             detCountyClassDict[key].countyData],
            axis=1, sort=True)

    return countyClassDict
