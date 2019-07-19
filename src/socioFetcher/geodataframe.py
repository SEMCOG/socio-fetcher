import pandas as pd


class GeoDataFrame:
    """ 
        A class to store data about specific geography, it
    can load, parse and export data fetched from APIs.

    Attributes: 
        county:str  The real part of complex number. 
        dataset:str  The imaginary part of complex number. 
        DataFrame:pandas.DataFrame    
                            DataFrame to store county data
    """

    def __init__(self, county, dataset="BLS"):
        """ 
            The constructor for GeoDataFrame class. 

        Parameters: 
           county:str   County Name 
           dataset:str   dataset type, must be one of BLS, BEA, 
                            BEA-GDP, or ACS 
        """
        self.county = county
        self.dataset = dataset
        #self.loadedBLSSeriesID = []
        self.DataFrame = pd.DataFrame()

    def __str__(self):
        self.__repr__ = self.__str__
        return self.county

    def load(self, data, source="BLS", year=None):
        """
            Load dict data response from API, and update 
        countyData

        Parameters:
            data:str   JSON object, dict
            source:str   one of "BLS", "BEA", and "Census"
            year:str   used in constructing ACS table

        Returns: 
            None
        """
        if source.upper() == "BLS" and self.dataset == "BLS":
            # self.loadedBLSSeriesID.append(data["seriesID"])
            parsedData = self.BLSParser(data)
            self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                       axis=1, sort=True)
        elif source.upper() == "BEA" and self.dataset == "BEA":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"])
            self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                       axis=1)
        elif source.upper() == "BEA-GDP" and self.dataset == "BEA-GDP":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"], gdp=True)
            if self.DataFrame.shape[0] == 0:
                self.DataFrame = parsedData
            else:
                self.DataFrame = self.DataFrame + parsedData
        elif source.upper() == "ACS" and self.dataset == "ACS":
            parsedData = self.ACSParser(data, year=year)  # check parser
            if self.DataFrame.shape[0] == 0:
                self.DataFrame = parsedData
            else:
                self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                           axis=0, sort=True)

    def BLSParser(self, data):
        """
        Generate Pandas Series from given JSON data, dict, from BLS

        Parameters
            data:dict   BLS JSON data

        Output: 
            pandas.Series
        """
        naicsCode = data["seriesID"][11:]  # NAICS code start at 12
        d = pd.Series(name=naicsCode)
        for dd in data['data']:
            if dd["period"] == "M13":
                d[dd["year"]] = int(dd["value"].replace(",", ""))
        return d

    def BEAParser(self, data, gdp=False):
        """
        Generate Pandas Series from given JSON data, dict, from BEA

        Parameters
            data:dict   BLS JSON data
            gdp:bolean  Parse GDP data, default is False

        Output: 
            pandas.Series
        """
        colName = "avgIncome" if not gdp else "GDP"
        d = pd.DataFrame(columns=[colName], dtype="float64")
        for dd in data["Data"]:
            d.loc[dd["TimePeriod"], colName] = float(
                dd["DataValue"].replace(",", ""))
        return d

    def ACSParser(self, data, year=None):
        """
        Generate Pandas Series from given JSON data, dict, from ACS

        Parameters
            data:dict   BLS JSON data
            year:str    Year of the ACS data

        Output: 
            pandas.Series
        """
        d = pd.DataFrame(data[1:], columns=data[0])
        d.index = [year]
        return d
