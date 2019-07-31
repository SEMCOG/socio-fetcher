from socioFetcher import Config, Downloader

# Customize Config
myConfig = Config()
myConfig.BLS.API_KEY = "YOUR_BLS_KEY"
myConfig.BLS.TABLE_NUMBER = ["ENU"]
myConfig.BLS.DATA_TYPE = ["1"]
myConfig.BLS.SIZE = ["0"]
myConfig.BLS.OWNERSHIP = ["5"]
myConfig.BLS.NAICS_CODE_LIST = {
    "10":	"10 Total, all industries",
    "101":	"101 Goods-producing",
    "102"	: "102 Service-providing"
}

myConfig.BEA.API_KDY = "YOUR_BEA_KEY"
myConfig.BEA.LINE_CODE = ["3"]
myConfig.BEA.TABLE_NAME = ["CAINC1"]
myConfig.BEA.YEAR = ["ALL"]

datasets = ["BLS", "BEA"]
fips = {"26093": "Livingston,MI",
        "26099": "Macomb,MI",
        "26115": "Monroe,MI",
        "26125": "Oakland,MI",
        "26147": "St. Clair,MI",
        "26161": "Washtenaw,MI",
        "26163": "Wayne,MI"}
dl = Downloader(datasets, list(fips.keys()), config=myConfig)
dl.download()
dl.export("data/")
