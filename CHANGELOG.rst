Change Log
==============

Expected use
--------------
::

    # config
    from socioFetcher import Config
    myConfig = Config()
    myConfig.show() # show current config
    myConfig.Global.areaCode = {...}
    myConfig.BLS.key = "key"
    myConfig.Census.key = "key"
    myConfig.BEA.key = "key"
    ...
    # download
    from socioFetcher import Downloader
    downloader = Downloader(["BEA", "BLS"], ["26193"], config=myConfig)
    downloader.download()
    # summarize
    downloader.sumerize(by="geography")
    # mapping in Jupyter notebook
    m = downloader.mapping(dataset="BEA")
    m.show()
    # export
    downloader.export("path/to/save/data",**kwargs)

Todo
--------------
- Migrate repo to SEMCOG account, 

Log
--------------
- 08/05 
    - Add BLS unEmployment data download feature,
    - add related config setting
    - Add export to json options
- 08/01 
    - Add gettingstarted and installation pages in docs
    - Remove all credentials in the config and edit .gitigonore to exclude test folder
    - Transfer the repo to SEMCOG account
- 07/31 Add doc session in root dir, add docstring in modules
- 07/30 
    - Improving BLS downloading and bug fixed
    - Added and tested MapView module, mapping data to the map
- 07/29 Finished and test mapping module. 91% cov
    - 📝Add year, attr select and data display widget in the map
    - 📝Add progress bar when downloading data
    - 🖇Edit test to reflect changes
- 07/26 📝Add func to produce choro data by attr and year
- 07/25 📝Add download geojson from Census REST feature, choro map, iteractive map, handling click.
- 07/24 
    - 🖇Rename Config api variables for better user understanding 
    - 🖇Remove redundant Config variable 
    - 🐞Fix a bug which cause produce repetitive record in DataFrame when fetching ACS data
    - 
- 07/23 Refactor downloader with request.Session
    - 🖇Refactor downloader using request.Session, improve profermance
- 07/22 🖇Refactor config.py to include a class to hold all config attributes
        🖇Edit testing files to reflect the changes in config
- 07/19 📝 Add unit test for downloader, add func test for download,
        fix bugs in BEA download
- 07/18 📝 Add summary and export feature to Downloader
    - Intergrate summary.py into Downloader
        - Sumerize by either geography or dataset
    - 📝Add export function to Downloader
        - export either individual file or summary
            file by either geography or dataset
    - 📝Add unit testing of geodataframe

- 07/17 🧹Rewrite download.py in Class format downloader.py
    - Downloader accept options in constructor
    - Use Downloader.download() func download data and save to Downloader.data
- 07/16 Set up the pakeage required files
