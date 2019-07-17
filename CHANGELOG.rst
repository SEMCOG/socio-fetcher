Change Log
==============
1. finalizing the tool
    1. make the api easy to use, intuitive, pakeage-ready
2.  writing test for the tools

Expected use
--------------
>>> from socioFetcher import Downloader
>>> downloader = Downloader(["BEA", "BLS"], ["26193"], **kwargs)
>>> downloader.download()
>>> downloader.data # downloaded data
>>> downloader.export("path/to/save/data",**kwargs)


Todo
--------------
- Intergrate summary.py into Downloader
- Testing geodataframe.py
- Testing downloader.py
- Testing summary.py

Log
--------------
- 07/17 Rewrite download.py in Class format downloader.py
    - Downloader accept options in constructor
    - Use Downloader.download() func download data and save to Downloader.data
- 07/16 Set up the pakeage required files
