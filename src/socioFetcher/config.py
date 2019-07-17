# ==========================================
#
#   Configration
#
# ------------------------------------------
#   Global
# ------------------------------------------
GLOBAL_OUTPUT_FOLDER = "data/output"
GLOBAL_OUTPUT_PICKLE_FOLDER = "data/pickles"
GLOBAL_OUTPUT_SUMMARY_FOLDER = "data/summary/"
GLOBAL_ALLOWED_DATASET = ["BLS", "BEA", "BEA-GDP", "ACS"]
GLOBAL_AREA_CODE = {"26093": "Livingston,MI",
                    "26099": "Macomb,MI",
                    "26115": "Monroe,MI",
                    "26125": "Oakland,MI",
                    "26147": "St. Clair,MI",
                    "26161": "Washtenaw,MI",
                    "26163": "Wayne,MI",
                    "11460": "Ann Arbor Metro",
                    "19820": "Detroit Metro",
                    "33780": "Monroe Metro"}
# ==========================================
# ------------------------------------------
#   BLS API configration
#   useage: 500 request per day, 50 series per query limit
# ------------------------------------------
# BLS api key
BLS_API_KEY = "5a0e1a49d56d402d8331feac501593dd"

# BLS Series ID List, https://data.bls.gov/, each
# represent a county.

BLS_TABLE_NUMBER = ["ENU"]  # QCEW Data
BLS_AREA_CODE = {"26093": "Livingston,MI",
                 "26099": "Macomb,MI",
                 "26115": "Monroe,MI",
                 "26125": "Oakland,MI",
                 "26147": "St. Clair,MI",
                 "26161": "Washtenaw,MI",
                 "26163": "Wayne,MI"}
BLS_DATA_TYPE = ["1"]  # All Employees
BLS_SIZE = ["0"]       # All size
BLS_OWNERSHIP = ["0"]  # All covered
BLS_NAICS_CODE_LIST = ["10"]
# Start and End year of query, eariest year is 2001
BLS_START_YEAR = "2001"
BLS_END_YEAR = "2018"

# ------------------------------------------
# BEA API configration
# user guide:
# https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf
# usage: 1000 API calls per minute
# ------------------------------------------
BEA_API_KEY = "4040651D-C3D5-4A2F-AEE5-23CD52AF863C"
BEA_GEO_FIPS = {"26093": "Livingston,MI",
                "26099": "Macomb,MI",
                "26115": "Monroe,MI",
                "26125": "Oakland,MI",
                "26147": "St. Clair,MI",
                "26161": "Washtenaw,MI",
                "26163": "Wayne,MI"}
BEA_LINE_CODE = ["3"]           # Per capita personal income (dollars) 2/
# Personal Income Summary: Personal Income, Population, Per Capita Personal Income
# https://apps.bea.gov/api/data/?&UserID=4040651D-C3D5-4A2F-AEE5-23CD52AF863C&method=getparametervalues&datasetname=Regionalproduct&parametername=industryid&dataformat=xml
# Personal Income Summary: Personal Income, Population, Per Capita Personal Income (Non-Industry)
BEA_TABLE_NAME = ["CAINC1"]
BEA_YEAR = ["ALL"]              # All year

BEA_GDP_METRO_CODE = {"11460": "Ann Arbor Metro",
                      "19820": "Detroit Metro",
                      "33780": "Monroe Metro"}
BEA_GDP_COMPONENT = ["RGDP_MAN"]  # Real GDP by metro
BEA_GDP_INDUSTRY = ["1"]        # total
BEA_GDP_YEAR = ["ALL"]          # all year
# ------------------------------------------
# Census ACS API configration
# TODO:fix census download
# ------------------------------------------
CENSUS_API_KEY = "a1b79f5105b689bd9c4ed357de83130393b6dec7"
CENSUS_YEAR = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]
# Subject url: https://api.census.gov/data/2017/acs/acs1/subject
CENSUS_SUBJECT_LIST = {
    # only available in ACS5
    "S0102_C01_036E": "Some college or associate's degree",
    # only available in ACS5
    "S0102_C01_037E": "Bachelor's degree or higher",
    "S0101_C01_001E": "Total population",
    "S0102_C01_087E": "Under proverty line",  # only available in ACS5
}
# Detail url: https://api.census.gov/data/2017/acs/acs1
CENSUS_DETAIL_LIST = {
    "C17016_001E": "Total Household",  # only in acs1
    "C17016_002E": "Household Below poverty level"  # only in acs1
}
CENSUS_COUNTY_CODE = {"093": "Livingston,MI",
                      "099": "Macomb,MI",
                      "115": "Monroe,MI",
                      "125": "Oakland,MI",
                      "147": "St. Clair,MI",
                      "161": "Washtenaw,MI",
                      "163": "Wayne,MI"}
CENSUS_STATE_CODE = ["26"]  # MI

# Export a dict containing all config
config = {
    "GLOBAL_OUTPUT_FOLDER": GLOBAL_OUTPUT_FOLDER,
    "GLOBAL_OUTPUT_PICKLE_FOLDER": GLOBAL_OUTPUT_PICKLE_FOLDER,
    "GLOBAL_OUTPUT_SUMMARY_FOLDER": GLOBAL_OUTPUT_SUMMARY_FOLDER,
    "GLOBAL_ALLOWED_DATASET": GLOBAL_ALLOWED_DATASET,
    "GLOBAL_AREA_CODE": GLOBAL_AREA_CODE,
    # BLS
    "BLS_API_KEY": BLS_API_KEY,
    "BLS_AREA_CODE": BLS_AREA_CODE,
    "BLS_DATA_TYPE": BLS_DATA_TYPE,
    "BLS_START_YEAR": BLS_START_YEAR,
    "BLS_END_YEAR": BLS_END_YEAR,
    "BLS_OWNERSHIP": BLS_OWNERSHIP,
    "BLS_SIZE": BLS_SIZE,
    "BLS_TABLE_NUMBER": BLS_TABLE_NUMBER,
    "BLS_NAICS_CODE_LIST": BLS_NAICS_CODE_LIST,
    # BEA
    "BEA_API_KEY": BEA_API_KEY,
    "BEA_GDP_COMPONENT": BEA_GDP_COMPONENT,
    "BEA_GDP_INDUSTRY": BEA_GDP_INDUSTRY,
    "BEA_GDP_METRO_CODE": BEA_GDP_METRO_CODE,
    "BEA_GDP_YEAR": BEA_GDP_YEAR,
    "BEA_GEO_FIPS": BEA_GEO_FIPS,
    "BEA_LINE_CODE": BEA_LINE_CODE,
    "BEA_TABLE_NAME": BEA_TABLE_NAME,
    "BEA_YEAR": BEA_YEAR,
    # Census
    "CENSUS_API_KEY": CENSUS_API_KEY,
    "CENSUS_COUNTY_CODE": CENSUS_COUNTY_CODE,
    "CENSUS_DETAIL_LIST": CENSUS_DETAIL_LIST,
    "CENSUS_STATE_CODE": CENSUS_STATE_CODE,
    "CENSUS_SUBJECT_LIST": CENSUS_SUBJECT_LIST,
    "CENSUS_YEAR": CENSUS_YEAR
}
