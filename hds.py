import os
import random
import re
import sys
import time
import zipfile

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

root_dir = os.getcwd()
data_dir = os.path.join(root_dir, 'data')
zip_dir = os.path.join(data_dir, 'zipped')
raw_dir = os.path.join(data_dir, 'raw')
out_dir = os.path.join(data_dir, 'output')


def scrap(output_folder):
    url = 'http://www.histdata.com/' \
          'download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes'
    options = Options()
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', output_folder)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
    driver = webdriver.Firefox(options=options, firefox_profile=profile)

    driver.get(url)
    forex_pair_urls = [element.get_attribute('href') for element in driver.find_elements_by_xpath(
        '//*[@class="page-content"]/table/tbody/tr/td/a')]
    for i, forex_pair_url in enumerate(forex_pair_urls):
        driver.get(forex_pair_url)
        date_urls = [element.get_attribute('href') for element in driver.find_elements_by_xpath(
            '//*[@class="page-content"]/p/a')]
        for j, date_url in enumerate(date_urls):
            driver.get(date_url)
            link = driver.find_element_by_id('a_file')
            link.click()
            print(
                '\r' + ' Download: ' + str(i + 1).zfill(len(str(len(forex_pair_urls)))) + '/' + str(
                    len(forex_pair_urls)) + ' forex pairs - ' + str(j + 1).zfill(
                    len(str(len(date_urls))))
                + '/' + str(len(date_urls)) + ' single files', end='', flush=True)
            time.sleep(random.randint(1, 3))
    print('\n')

    driver.get('about:downloads')
    while True:
        time.sleep(5)
        active = driver.find_elements_by_css_selector('button.downloadButton.downloadIconCancel')
        if len(active) == 0:
            break
    driver.quit()


def extract(input_folder, output_folder):
    files = os.listdir(input_folder)
    for i, file in enumerate(files):
        if file.endswith('.zip'):
            file = os.path.join(input_folder, file)
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
        print('\r' + ' Extracting: ' + str(i + 1).zfill(len(str(len(files)))) + '/' + str(
            len(files)), end='', flush=True)
    print('\n')


def merge(input_folder, output_folder):
    csv_files = [a for a in os.listdir(input_folder) if a.endswith('.csv')]
    csv_files.sort()
    for i, csv_file in enumerate(csv_files):
        reg = re.compile('.+(?=_\\d*)')
        with open(os.path.join(output_folder, reg.match(csv_file).group() + '.csv'), 'a') as outfile:
            csv_file = os.path.join(input_folder, csv_file)
            with open(csv_file) as infile:
                for line in infile:
                    outfile.write(line)
        print('\r' + ' Merging: ' + str(i + 1).zfill(len(str(len(csv_files)))) + '/'
              + str(len(csv_files)), end='', flush=True)
    print('\n')


def main():
    if len(sys.argv) is 1 or len(sys.argv) is 2:
        if len(sys.argv) is 1 or 's' in sys.argv[1]:
            os.makedirs(zip_dir, exist_ok=True)
            for old_file in os.listdir(zip_dir):
                old_file = os.path.join(zip_dir, old_file)
                os.remove(old_file)
            scrap(zip_dir)
        if len(sys.argv) is 1 or 'e' in sys.argv[1]:
            os.makedirs(zip_dir, exist_ok=True)
            os.makedirs(raw_dir, exist_ok=True)
            for old_file in os.listdir(raw_dir):
                old_file = os.path.join(raw_dir, old_file)
                os.remove(old_file)
            extract(zip_dir, raw_dir)
        if len(sys.argv) is 1 or 'm' in sys.argv[1]:
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(out_dir, exist_ok=True)
            for old_file in os.listdir(out_dir):
                old_file = os.path.join(out_dir, old_file)
                os.remove(old_file)
            merge(raw_dir, out_dir)


if __name__ == '__main__':
    main()
