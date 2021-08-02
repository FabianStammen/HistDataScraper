"""HistDataScraper
A simple web scraper that downloads forex history data from HistData.
After the download the zip-files get extracted and then merged, based upon the forex pair.
The scraper can run without any parameters and will create an appropriate directory structure from
working directory.

When only a specific task should be executed you can give the program a parameter.
This parameter is a combination of any of the letter s(scrape), e(extract) and m(merge) without a
specific order.
Additional you can add an f(full) to the parameter to do a cleanup of old files before the tasks are
executed,
default is only incremental downloads and extractions. Merges are always full.

Example:
    If you just want to extract all zip folders and merge them the program call would be:

        $ python hds.py em

It is required to have firefox installed and a version of geckodriver in the same folder as the
program. (https://github.com/mozilla/geckodriver/releases\).
"""
import os
import re
import sys
import time
import zipfile
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def setup_driver(download_dir):
    """Setup the firefox geckodriver to be headless and proper options for downloading.

    Args:
        download_dir (str): The path to the new default download folder.

    Returns:
        selenium.webdriver.Firefox: The setup geckodriver.
    """
    options = Options()
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
    return webdriver.Firefox(options=options, firefox_profile=profile)


def scrap(output_folder, full=False):
    """Scrap the Forex data from the web.

    Args:
        output_folder: Path to the download folder.
        full (bool): Full download or incremental; default false.
    """
    base_url = 'https://www.histdata.com'
    url = base_url + '/download-free-forex-data/?/metastock/1-minute-bar-quotes'
    driver = setup_driver(output_folder)
    commodities = ['WTI/USD', 'BCO/USD']
    indexes = ['SPX/USD', 'JPX/JPY', 'NSX/USD', 'FRX/EUR', 'UDX/USD',
               'UKX/GBP', 'GRX/EUR', 'AUX/AUD', 'HKX/HKD', 'ETX/EUR']

    os.makedirs(output_folder, exist_ok=True)
    last_file = ''
    to_be_removed = set()
    current_year = datetime.now().year
    for old_file in sorted(os.listdir(output_folder)):
        if full:
            os.remove(os.path.join(output_folder, old_file))
        elif '.part' in old_file:
            to_be_removed.add(old_file)
            to_be_removed.add(old_file[:-5])
        elif len(old_file) == 35 and int(old_file[25:-6]) < current_year:
            to_be_removed.add(old_file)
        elif last_file != '' and last_file[:22] != old_file[:22]:
            to_be_removed.add(last_file)
        last_file = old_file
    for part in to_be_removed:
        if os.path.exists(os.path.join(output_folder, part)):
            os.remove(os.path.join(output_folder, part))

    forex_pair_urls = [tag.get('href') for tag in BeautifulSoup(requests.get(url).text, 'lxml')
                       .find(class_='page-content').select('a[title]')
                       if tag.get_text() not in commodities and tag.get_text() not in indexes]
    for i, forex_pair_url in enumerate(forex_pair_urls):
        date_urls = [tag.get('href') for tag in BeautifulSoup(requests.get(
            base_url + forex_pair_url).text, 'lxml').find(class_='page-content').select('a[title]')]
        for j, date_url in enumerate(date_urls):
            link = BeautifulSoup(requests.get(base_url + date_url).text, 'lxml').find(id='a_file')
            if ''.join(link.get_text().rsplit('_', 1)) not in os.listdir(output_folder):
                driver.get(base_url + date_url)
                driver.execute_script('jQuery("#file_down").submit();')
            print(
                '\r' + ' Download: ' + str(i + 1).zfill(len(str(len(forex_pair_urls)))) + '/' + str(
                    len(forex_pair_urls)) + ' forex pairs - ' + str(j + 1).zfill(
                        len(str(len(date_urls))))
                + '/' + str(len(date_urls)) + ' single files', end='', flush=True)
    print('\n')

    driver.get('about:downloads')
    while True:
        time.sleep(5)
        if not driver.find_elements_by_css_selector('button.downloadButton.downloadIconCancel'):
            break
    driver.quit()


def extract(input_folder, output_folder, full=False):
    """Extract the downloaded csv files.

    Args:
        input_folder (str): Path to input folder.
        output_folder (str): Path to output folder.
        full (bool): Full extraction or incremental; default false.
    """
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    if full:
        for old_file in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, old_file))

    files = os.listdir(input_folder)
    for i, file in enumerate(files):
        if file.endswith('.zip'):
            if file[:-4] + '.csv' not in os.listdir(output_folder):
                file = os.path.join(input_folder, file)
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(output_folder)
        print('\r' + ' Extracting: ' + str(i + 1).zfill(len(str(len(files)))) + '/' + str(
            len(files)), end='', flush=True)
    print('\n')


def merge(input_folder, output_folder):
    """Merges the extracted csv files according to their currency-pair.

    Args:
        input_folder (str): Path to input folder.
        output_folder (str): Path to output folder.
    """
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    for old_file in os.listdir(output_folder):
        old_file = os.path.join(output_folder, old_file)
        os.remove(old_file)
    csv_files = [a for a in os.listdir(input_folder) if a.endswith('.csv')]
    csv_files.sort()
    for i, csv_file in enumerate(csv_files):
        reg = re.compile('.+(?=_\\d*)')
        with open(os.path.join(output_folder, reg.match(csv_file).group() + '.csv'),
                  'a') as outfile:
            csv_file = os.path.join(input_folder, csv_file)
            with open(csv_file) as infile:
                for line in infile:
                    outfile.write(line)
        print('\r' + ' Merging: ' + str(i + 1).zfill(len(str(len(csv_files)))) + '/'
              + str(len(csv_files)), end='', flush=True)
    print('\n')


def main():
    """Main function

    Checks for any system arguments described in the module documentation and initializes the
    module.
    """
    root_dir = os.getcwd()
    data_dir = os.path.join(root_dir, 'data')
    zip_dir = os.path.join(data_dir, 'zipped')
    raw_dir = os.path.join(data_dir, 'raw')
    out_dir = os.path.join(data_dir, 'output')

    if len(sys.argv) == 1:
        scrap(zip_dir, False)
        extract(zip_dir, raw_dir, False)
        merge(raw_dir, out_dir)
    if len(sys.argv) == 2:
        if 's' in sys.argv[1]:
            scrap(zip_dir, 'f' in sys.argv[1])
        if 'e' in sys.argv[1]:
            extract(zip_dir, raw_dir, 'f' in sys.argv[1])
        if 'm' in sys.argv[1]:
            merge(raw_dir, out_dir)


if __name__ == '__main__':
    main()
