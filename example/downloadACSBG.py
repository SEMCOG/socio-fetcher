from socioFetcher import Config, Downloader
myConfig = Config()
myConfig.ACS.API_KEY = "YOUR_ACS_KEY"
myConfig.ACS.YEAR = [ "2017", "2018"]
myConfig.ACS.FIELDS = [
{
    "data": "acs",
    "id": "B25002_002E",
    "desc": "Total Occupied Household",
    "availability": {
        "subcategory": "acs5",
        "subject": False
    }
},
{
    "data": "acs",
    "id": "B25001_001E",
    "desc": "Housing Unit",
    "availability": {
        "subcategory": "acs5",
        "subject": False
    }
},
]
datasets = ["ACS_BG"]
fips = {"26093": "Livingston,MI"}
dl = Downloader(datasets, list(fips.keys()), config=myConfig)
dl.download()
dl.export("data/", saveformat="csv", by="block group")