HistDataScraper
A simple web scraper that downloads forex history data from HistData.

After the download the zip-files get extracted and then merged, based upon the forex pair.

The scraper can run without any parameters and will create an appropriate directory structure from working directory.

working directory
      -data
            -zipped
            -raw
            -output

When only a specific task should be executed you can give the program a parameter.
This parameter is a combination of any of the letter s(scrape), e(extract) and m(merge) without a specific order.
Additional you can add an f(full) to the parameter to do a cleanup of old files before the tasks are executed,
default is only incremental downloads and extractions. Merges are always full.

For example If you just want to extract all zip folders and merge them the program call would be: 'python hds.py em'.

It is required to have firefox installed and a version of geckodriver in the path or same folder as the program. (https://github.com/mozilla/geckodriver/releases\).\ All other requirements are within requirements.txt.
You can easily install them with 'pip install -r requirements.txt'.
