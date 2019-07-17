import os
from socioFetcher.config import *
from socioFetcher.download import *
from socioFetcher.summary import *
import pickle


def main():
    if os.path.exists(os.path.join(GLOBAL_GLOBAL_OUTPUT_PICKLE_FOLDER, "BLS.pickle")):
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "BLS.pickle"), "rb") as f:
            BLSdata = pickle.load(f)
    else:
        BLSdata = BLSdownload()
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "BLS.pickle"), "wb") as f:
            pickle.dump(BLSdata, f)

    if os.path.exists(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "BEA.pickle")):
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "BEA.pickle"), "rb") as f:
            BEAdata = pickle.load(f)
    else:
        BEAdata = BEAIncomeDownload()
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "BEA.pickle"), "wb") as f:
            pickle.dump(BEAdata, f)

    if os.path.exists(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "ACS.pickle")):
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "ACS.pickle"), "rb") as f:
            ACSdata = pickle.load(f)
    else:
        ACSdata = ACSDownload()
        with open(os.path.join(GLOBAL_OUTPUT_PICKLE_FOLDER, "ACS.pickle"), "wb") as f:
            pickle.dump(ACSdata, f)

    countySummaryDict = getCountySummay(BLSdata, BEAdata, ACSdata)
    for key, item in countySummaryDict.items():
        item.to_csv(os.path.join(GLOBAL_OUTPUT_FOLDER, f"SUM{key}.csv"))


if __name__ == "__main__":
    main()
