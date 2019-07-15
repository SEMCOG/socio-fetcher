# TODO: Generate summary table from result dataframe
import pandas as pd
from utils.config import *


def getBLSTotalTable(countyClassDict):
    """
    Generate a table containing total number of 
    employment for each county in each year.
    -----
    Parameter:
    countyClassDict dict each item is a Pandas Dataframe

    -----
    Return: A pandas dataframe
    """
    # total NAICS code: "10"
    totalTable = pd.DataFrame()
    for countyID, countyClass in countyClassDict.items():
        # "10" represent the total
        localTotalTable = countyClass.countyData.loc[:, ["10"]]
        localTotalTable.columns = [BLS_AREA_CODE[countyID]]
        totalTable = pd.concat([totalTable, localTotalTable],
                               axis=1, sort=True)
    return totalTable


def getBEAIncomeTable(countyClassDict):
    """
    Generate a table containing per capita income
     for each county in each year.
    -----
    Parameter:
    countyClassDict dict each item is a Pandas Dataframe

    -----
    Return: A pandas dataframe
    """
    incomeTable = pd.DataFrame()
    for countyID, countyClass in countyClassDict.items():
        # "10" represent the total
        localIncomeTable = countyClass.countyData
        localIncomeTable.columns = [BEA_GEO_FIPS[countyID]]
        incomeTable = pd.concat([incomeTable, localIncomeTable],
                                axis=1, sort=True)
    return incomeTable


def getBEAGDPTable(GDPdata):
    return GDPdata


def getCountySummay(BLSdata, BEAdata, ACSdata):
    countyAggDict = {}
    for countyID, name in BLS_AREA_CODE.items():
        countyAggDict[countyID] = pd.concat(
            [BLSdata[countyID].countyData,
             BEAdata[countyID].countyData,
             ACSdata[countyID].countyData
             ], axis=1, sort=True
        )
    return countyAggDict
