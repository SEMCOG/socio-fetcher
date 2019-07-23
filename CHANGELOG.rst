Change Log
==============
1. finalizing the tool
    1. make the api easy to use, intuitive, pakeage-ready
2.  writing test for the tools

Expected use
--------------
::

    # config
    from socioFetcher import Config
    myConfig = Config()
    myConfig.show() # show current config
    myConfig.Global.areaCode = {...}
    myConfig.BLS.key = "key"
    ...
    # download
    from socioFetcher import Downloader
    downloader = Downloader(["BEA", "BLS"], ["26193"], config=myConfig)
    downloader.download()
    downloader.data # downloaded data
    # summarize
    downloader.sumerize(by="geography")
    # export
    downloader.export("path/to/save/data",**kwargs)

Todo
--------------
- Simplify config api by including us module ???
    us only include state level info
- Testing summary.py

Log
--------------
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
