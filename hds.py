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
    options = Options()
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
    return webdriver.Firefox(options=options, firefox_profile=profile)


def scrap(output_folder, full=False):
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
