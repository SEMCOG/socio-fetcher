# ==========================================
#
#   Configration
# ==========================================


class Global:
    """
    Class to hold all Global settings for the downloader

    Attributes
    ----------
    ALLOWED_DATASET : list of str
        Allowed dataset options supported by this library
    FIPS_CODE : dict  {fipsCode=>Name}
        Python dictionary with fips code as key and name
        as values
    """

    def __init__(self):
        self.ALLOWED_DATASET = ["BLS", "BEA", "BEAGDP", "ACS"]
        self.FIPS_CODE = {"26093": "Livingston,MI",
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
    """
    Class to hold all BLS settings for the downloader

    Attributes
    ----------
    API_KEY : str, required
        API key for BLS api
    TABLE_NUMBER : list of str
        Table number list to download
    NAICS_CODE_LIST : dict  {naics_code=>naics_name}
        The naics code to download from BLS
    DATA_TYPE : list of str
        Data type to download
    SIZE : list of str
        Size category to download
    OWNERSHIP : list of str
        Ownership type to download
    START_YEAR : str
        Start year of the query 
    END_YEAR : str
        End year of the query
    """

    def __init__(self):
        self.API_KEY = None

        # BLS Series ID List, https://data.bls.gov/, each
        # represent a county.

        self.TABLE_NUMBER = ["ENU"]  # QCEW Data
        self.DATA_TYPE = ["1"]  # All Employees
        self.SIZE = ["0"]       # All size
        self.OWNERSHIP = ["5"]  # Private
        self.NAICS_CODE_LIST = {
            "10":	"10 Total, all industries",
            "101":	"101 Goods-producing",
            "1011"	: "1011 Natural resources and mining",
            "1012"	: "1012 Construction",
            "1013"	: "1013 Manufacturing",
            "102"	: "102 Service-providing",
            "1021"	: "1021 Trade, transportation, and utilities",
            "1022"	: "1022 Information",
            "1023"	: "1023 Financial activities",
            "1024"	: "1024 Professional and business services",
            "1025"	: "1025 Education and health services",
            "1026"	: "1026 Leisure and hospitality",
            "1027"	: "1027 Other services",
            "1029"	: "1029 Unclassified"
        }
        # Start and End year of query, eariest year is 2001
        self.START_YEAR = "2001"
        self.END_YEAR = "2018"


class BEA:
    """
    Class to hold all BEA settings for the downloader

    Attributes
    ----------
    API_KEY : str, required
        API key for BEA api
    LINE_CODE : list of str
        Line Code list to download, defalt is ["3"]
    TABLE_NAME : list of str
        Table name to download, default is ["CAINC1"]
    YEAR : list of str
        Years to download, default is ["ALL"]
    GDP_METRO_CODE : dict {metroFipsCode=>metroName}
        Metro fips code to download (GDP data only)
    GDP_COMPONENT : list of str
        GDP component attribute, default is ["RGDP_MAN"]
    GDP_INDUSTRY : list of str
        Industry code to download, default is ["1"] (total)
    GDP_YEAR : list of str
        Year to download for GDP data, default is ["ALL"]

    """

    def __init__(self):
        self.API_KEY = None
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
    """
    Class to hold all ACS(Census) settings for the downloader

    Attributes
    ----------
    API_KEY : str, required
        API key for ACS(Census) api
    YEAR : list of str
        Year list to download ACS data, defualt is ["2010", "2011", "2012",
        "2013", "2014", "2015", "2016", "2017"]
    SUBJECT_LIST : dict  {SUBJECT_ID=>SUBJECT_NAME}
        Subject id list to download, default is {
            # only available in ACS5
            "S0102_C01_036E": "Some college or associate's degree",
            # only available in ACS5
            "S0102_C01_037E": "Bachelor's degree or higher",
            "S0101_C01_001E": "Total population",
            "S0102_C01_087E": "Under proverty line",  # only available in ACS5
        }
    DETAIL_LIST : dict  {Detail_ID=>Detail_NAME}
        Detail id list to download, default is {
            "C17016_001E": "Total Household",  # only in acs1
            "C17016_002E": "Household Below poverty level"  # only in acs1
        }

    """

    def __init__(self):
        self.API_KEY = None
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


class Config:
    """
    Class to hold all ACS(Census) settings for the downloader

    Attributes
    ----------
    Global : socioFetcher.config.Global
    BLS : socioFetcher.config.BLS
    BEA : socioFetcher.config.BEA
    Census : socioFetcher.config.Census

    """

    def __init__(self):
        self.Global = Global()
        self.BLS = BLS()
        self.BEA = BEA()
        self.Census = Census()
