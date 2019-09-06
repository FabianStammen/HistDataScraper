# HistDataScraper
A simple web scraper that downloads forex history data from HistData.

At the moment only the 1-minute data for Metatrader 4/5 is downloaded.\
After the download the zip-files get extracted and then merged, based upon the forex pair.

The scraper can run without ana parameters and will create an appropriate directory structure from working directory.

working directory\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-data\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-zipped\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-raw\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-output
    
When only a specific task should be executed you can give the program a parameter.\
This parameter is a combination of any of the letter s(scrape), e(extract) and m(merge) without a specific order.\
Additional you can add an f(full) to the parameter to do a cleanup of old files before the tasks are executed,\
default is only incremental downloads and extractions. Merges are always full.

For example If you just want to extract all zip folders and merge them the program call would be: 'python hds.py em'.

It is required to have firefox installed and a version of geckodriver in the same folder as the program. (https://github.com/mozilla/geckodriver/releases\).\
All other requirements are within requirements.txt.\
You can easily install them with 'pip install -r requirements.txt'.
