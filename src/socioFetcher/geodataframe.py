import pandas as pd


class GeoDataFrame:
    """ 
    A class to store data about specific geography, it
    can load, parse and export data fetched from APIs.

    Attributes
    -----------
    county:str
        The real part of complex number. 
    dataset:str
        The imaginary part of complex number. 
    DataFrame:pandas.DataFrame    
        DataFrame to store county data

    """

    def __init__(self, county, dataset="BLS"):
        """ 
            The constructor for GeoDataFrame class. 

        Parameters
        ----------
        county:str
            County Name 
        dataset:str
            dataset type, must be one of BLS, BEA, 
                        BEAGDP, or ACS 
        """
        self.county = county
        self.dataset = dataset
        #self.loadedBLSSeriesID = []
        self.DataFrame = pd.DataFrame()
        self._tempDataFrame = pd.DataFrame()
        self._lastLoadedYear = None

    def __str__(self):
        self.__repr__ = self.__str__
        return self.county

    def load(self, data, source="BLS", year=None):
        """
        Load dict data response from API, and update 
        countyData

        Parameters
        ----------
        data:str
           JSON object, dict
        source:str
           one of "BLS", "BEA", and "Census"
        year:str
           used in constructing ACS table

        Returns
        ----------
            None

        """
        if source.upper() == "BLS" and self.dataset == "BLS":
            # self.loadedBLSSeriesID.append(data["seriesID"])
            parsedData = self.BLSParser(data)
            self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                       axis=1, sort=True)
            self.DataFrame = self.DataFrame.fillna(method='ffill')
            self.DataFrame = self.DataFrame.fillna(0)
        elif source.upper() == "BEA" and self.dataset == "BEA":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"])
            self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                       axis=1, sort=True)
        elif source.upper() == "BEAGDP" and self.dataset == "BEAGDP":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"], gdp=True)
            if self.DataFrame.shape[0] == 0:
                self.DataFrame = parsedData
            else:
                self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                           axis=1, sort=True)
        elif source.upper() == "ACS" and self.dataset == "ACS":
            parsedData = self.ACSParser(data, year=year)
            # if temp dataframe is empty, assign parsed to temp df
            if year in self._tempDataFrame.index or self._lastLoadedYear == None:

                self._tempDataFrame = pd.concat([self._tempDataFrame, parsedData],
                                                axis=1, sort=True)
                # if reach the end then merge temp and master
                if len(self._tempDataFrame.columns) == len(self.DataFrame.columns):
                    self.DataFrame = pd.concat([self.DataFrame, self._tempDataFrame],
                                               axis=0)
                    self._tempDataFrame = pd.DataFrame()
                self._lastLoadedYear = year

            # else if new year data comming, append temp df to master df, and
            # assign new year data to temp df
            else:  # year not in self._tempDataFrame.index
                # If master df is empty, assign temp to master and assign
                # parsedData to temp
                if self.DataFrame.shape[0] == 0:
                    self.DataFrame = self._tempDataFrame
                    self._tempDataFrame = parsedData
                # else merge temp and master
                else:
                    self.DataFrame = pd.concat([self.DataFrame, self._tempDataFrame],
                                               axis=0)
                    self._tempDataFrame = parsedData
                if len(parsedData.columns) == len(self.DataFrame.columns):
                    self.DataFrame = pd.concat([self.DataFrame, parsedData],
                                               axis=0)
                    self._tempDataFrame = pd.DataFrame()
                #self.DataFrame = self.DataFrame.drop_duplicates()

    def BLSParser(self, data):
        """
        Generate Pandas Series from given JSON data, dict, from BLS

        Parameters
        ------------
        data:dict
            BLS JSON data

        Output
        ------------
        pandas.Series
        """
        attrName = data["seriesID"][-2:] if data["seriesID"][11] == "0" else data["seriesID"][11:]
        d = pd.Series(name=attrName)
        for dd in data['data']:
            if dd["period"] == "M13":
                try:
                    d[dd["year"]] = float(dd["value"].replace(",", ""))
                except:
                    Warning(f"Unable to parse {dd['value']} in {dd['year']}")
                    d[dd["year"]] = 0
        return d

    def BEAParser(self, data, gdp=False):
        """
        Generate Pandas Series from given JSON data, dict, from BEA

        Parameters
        ----------
        data:dict
            BLS JSON data
        gdp:bolean
            Parse GDP data, default is False

        Output
        ----------
        pandas.Series
        """
        colName = data["Statistic"]
        d = pd.DataFrame(columns=[colName], dtype="float64")
        for dd in data["Data"]:
            # if surpressed, default to -1
            try:
                d.loc[dd["TimePeriod"], colName] = float(
                    dd["DataValue"].replace(",", ""))
            except ValueError:
                d.loc[dd["TimePeriod"], colName] = -1.0
        return d

    def ACSParser(self, data, year=None):
        """
        Generate Pandas Series from given JSON data, dict, from ACS

        Parameters
        -----------
        data:dict
            ACS JSON data
        year:str
            Year of the ACS data

        Output
        ------------
            pandas.Series
        """
        d = pd.DataFrame(data[1:], columns=data[0], dtype='float')
        d.index = [year]
        return d
