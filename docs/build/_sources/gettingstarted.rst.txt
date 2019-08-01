Getting Started
===================

socioFetcher is a tool integrating python wrappers for BLS, BEA,
and Census API and interactive visualization tool. socioFetcher
use ``requests`` for sending requests to the APIs, use ``ipyleaflet``
to visualizing the downloaded data.

Before start, make sure install the package following the installation
page.

Customize Config
---------------------
We need to let the tool knows what we are looking for and provide
required information for compiling the requests to the API. We start
from import come core class object from ``socioFetcher``:
::

  from socioFetcher import Config, Downloader

After importing ``Config``, we should create an object from it call
``myConfig`` and customize it based on our need. But first, we need
to provide required api_key for each requested dataset.
::

  myConfig = Config()
  myConfig.BLS.API_KEY = "bls_api_key_goes_here"
  myConfig.BEA.API_KEY = "bea_api_key_goes_here"
  myConfig.Census.API_KEY = "census_api_key_goes_here"

For each requested dataset, we may provide information on what
table/data we are looking for. For more detail about the required
format of individual configration, please checkout
Reference session in the docs. Here are all available configration
for each dataset.

===============  ===============  ============
BLS                 BEA            Census
---------------  ---------------  ------------
TABLE_NUMBER     LINE_CODE        YEAR
NAICS_CODE_LIST  TABLE_NAME       SUBJECT_LIST
DATA_TYPE        YEAR             DETAIL_LIST
SIZE             GDP_METRO_CODE
OWNERSHIP        GDP_COMPONENT
START_YEAR       GDP_INDUSTRY
END_YEAR         GDP_YEAR
===============  ===============  ============

**Customize Configration**
::

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

Download raw data
---------------------
::

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

Download summary data
-----------------------
::

    # export summary by geography
    dl.export("summary/", summarize=True, by="geography")
    # export summary by dataset
    dl.export("summary/", summarize=True, by="dataset")

Visualization with ipyleaflet
------------------------------
::

    # in Jupyter notebook, ipython environment
    mapView = dl.mapping("BLS")
    mapView.show(
        center=(42.346814, -83.319304),
        zoom=8,
    )

