# ==========================================
#
#   Configration
# ==========================================


class Global:
    def __init__(self):
        self.OUTPUT_FOLDER = "data/output"
        self.OUTPUT_PICKLE_FOLDER = "data/pickles"
        self.OUTPUT_SUMMARY_FOLDER = "data/summary/"
        self.ALLOWED_DATASET = ["BLS", "BEA", "BEAGDP", "ACS"]
        self.AREA_CODE = {"26093": "Livingston,MI",
                          "26099": "Macomb,MI",
                          "26115": "Monroe,MI",
                          "26125": "Oakland,MI",
                          "26147": "St. Clair,MI",
                          "26161": "Washtenaw,MI",
                          "26163": "Wayne,MI",
                          "11460": "Ann Arbor Metro",
                          "19820": "Detroit Metro",
                          "33780": "Monroe Metro"}


class BLS:
    def __init__(self):
        self.API_KEY = "5a0e1a49d56d402d8331feac501593dd"

        # BLS Series ID List, https://data.bls.gov/, each
        # represent a county.

        self.TABLE_NUMBER = ["ENU"]  # QCEW Data
        self.AREA_CODE = {"26093": "Livingston,MI",
                          "26099": "Macomb,MI",
                          "26115": "Monroe,MI",
                          "26125": "Oakland,MI",
                          "26147": "St. Clair,MI",
                          "26161": "Washtenaw,MI",
                          "26163": "Wayne,MI"}
        self.DATA_TYPE = ["1"]  # All Employees
        self.SIZE = ["0"]       # All size
        self.OWNERSHIP = ["0"]  # All covered
        self.NAICS_CODE_LIST = ["10"]
        # Start and End year of query, eariest year is 2001
        self.START_YEAR = "2001"
        self.END_YEAR = "2018"


class BEA:
    def __init__(self):
        self.API_KEY = "4040651D-C3D5-4A2F-AEE5-23CD52AF863C"
        self.GEO_FIPS = {"26093": "Livingston,MI",
                         "26099": "Macomb,MI",
                         "26115": "Monroe,MI",
                         "26125": "Oakland,MI",
                         "26147": "St. Clair,MI",
                         "26161": "Washtenaw,MI",
                         "26163": "Wayne,MI"}
        # Per capita personal income (dollars) 2/
        self.LINE_CODE = ["3"]
        # Personal Income Summary: Personal Income, Population, Per Capita Personal Income
        # https://apps.bea.gov/api/data/?&UserID=4040651D-C3D5-4A2F-AEE5-23CD52AF863C&method=getparametervalues&datasetname=Regionalproduct&parametername=industryid&dataformat=xml
        # Personal Income Summary: Personal Income, Population, Per Capita Personal Income (Non-Industry)
        self.TABLE_NAME = ["CAINC1"]
        self.YEAR = ["ALL"]              # All year

        self.GDP_METRO_CODE = {"11460": "Ann Arbor Metro",
                               "19820": "Detroit Metro",
                               "33780": "Monroe Metro"}
        self.GDP_COMPONENT = ["RGDP_MAN"]  # Real GDP by metro
        self.GDP_INDUSTRY = ["1"]        # total
        self.GDP_YEAR = ["ALL"]          # all year


class Census:
    def __init__(self):
        self.API_KEY = "a1b79f5105b689bd9c4ed357de83130393b6dec7"
        self.YEAR = ["2010", "2011", "2012",
                     "2013", "2014", "2015", "2016", "2017"]
        # Subject url: https://api.census.gov/data/2017/acs/acs1/subject
        self.SUBJECT_LIST = {
            # only available in ACS5
            "S0102_C01_036E": "Some college or associate's degree",
            # only available in ACS5
            "S0102_C01_037E": "Bachelor's degree or higher",
            "S0101_C01_001E": "Total population",
            "S0102_C01_087E": "Under proverty line",  # only available in ACS5
        }
        # Detail url: https://api.census.gov/data/2017/acs/acs1
        self.DETAIL_LIST = {
            "C17016_001E": "Total Household",  # only in acs1
            "C17016_002E": "Household Below poverty level"  # only in acs1
        }
        self.COUNTY_CODE = {"093": "Livingston,MI",
                            "099": "Macomb,MI",
                            "115": "Monroe,MI",
                            "125": "Oakland,MI",
                            "147": "St. Clair,MI",
                            "161": "Washtenaw,MI",
                            "163": "Wayne,MI"}
        self.STATE_CODE = ["26"]  # MI


class Config:
    def __init__(self):
        self.Global = Global()
        self.BLS = BLS()
        self.BEA = BEA()
        self.Census = Census()
