import pandas as pd


class CountyDataFrame:
    """
    A Pandas DataFrame to hold annual county employment
    number data for NAICSs code.
    """

    def __init__(self, county, acceptData="BLS"):
        self.county = county
        self.acceptData = acceptData
        self.loadedBLSSeriesID = []
        self.countyData = pd.DataFrame()

    def __str__(self):
        self.__repr__ = self.__str__
        return self.county

    def get_county_name(self):
        return self.county

    def load(self, data, source="BLS", year=None):
        """
        Load dict data response from API, and update 
        countyData

        Parameters
        :data   str   JSON object, dict
        :source str   one of "BLS", "BEA", and "Census"
        :year   str   used in constructing ACS table
        -----
        Output: None
        """
        if source.upper() == "BLS" and self.acceptData == "BLS":
            self.loadedBLSSeriesID.append(data["seriesID"])
            parsedData = self.BLSParser(data)
            self.countyData = pd.concat([self.countyData, parsedData],
                                        axis=1, sort=True)
        elif source.upper() == "BEA" and self.acceptData == "BEA":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"])
            self.countyData = pd.concat([self.countyData, parsedData],
                                        axis=1, sort=True)
        elif source.upper() == "BEA-GDP" and self.acceptData == "BEA-GDP":
            parsedData = self.BEAParser(data["BEAAPI"]["Results"], gdp=True)
            if self.countyData.shape[0] == 0:
                self.countyData = parsedData
            else:
                self.countyData = self.countyData + parsedData
        elif source.upper() == "ACS" and self.acceptData == "ACS":
            parsedData = self.ACSParser(data, year=year)  # check parser
            if self.countyData.shape[0] == 0:
                self.countyData = parsedData
            else:
                self.countyData = pd.concat([self.countyData, parsedData],
                                            axis=0, sort=True)

    def BLSParser(self, data):
        """
        Generate Pandas Series from given JSON data, dict, from BLS

        Parameters
        :data   dict
        -----
        Output: Pandas Series
        """
        naicsCode = data["seriesID"][11:]  # NAICS code start at 12
        d = pd.Series(name=naicsCode)
        for dd in data['data']:
            if dd["period"] == "M13":
                d[dd["year"]] = int(dd["value"].replace(",", ""))
        return d

    def BEAParser(self, data, gdp=False):
        if not gdp:
            d = pd.DataFrame(columns=["avgIncome"], dtype="float64")
        else:
            d = pd.DataFrame(columns=["GDP"], dtype="float64")
        for dd in data["Data"]:
            d.loc[dd["TimePeriod"], "GDP"] = float(
                dd["DataValue"].replace(",", ""))
        return d

    def ACSParser(self, data, year=None):
        d = pd.DataFrame(data[1:], columns=data[0])
        d.index = [year]
        return d
