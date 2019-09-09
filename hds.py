import os
import re
import sys
import time
import zipfile

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def scrap(output_folder, full=False):
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

    os.makedirs(output_folder, exist_ok=True)
    to_be_removed = set()
    for old_file in os.listdir(output_folder):
        if full:
            os.remove(os.path.join(output_folder, old_file))
        if '.part' in old_file:
            to_be_removed.add(old_file)
            to_be_removed.add(old_file[:-5])
    for part in to_be_removed:
        if os.path.exists(os.path.join(output_folder, part)):
            os.remove(os.path.join(output_folder, part))

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
            if ''.join(link.text.rsplit('_', 1)) not in os.listdir(output_folder):
                link.click()
                time.sleep(1)
            print(
                '\r' + ' Download: ' + str(i + 1).zfill(len(str(len(forex_pair_urls)))) + '/' + str(
                    len(forex_pair_urls)) + ' forex pairs - ' + str(j + 1).zfill(
                    len(str(len(date_urls))))
                + '/' + str(len(date_urls)) + ' single files', end='', flush=True)
    print('\n')

    driver.get('about:downloads')
    while True:
        time.sleep(5)
        active = driver.find_elements_by_css_selector('button.downloadButton.downloadIconCancel')
        if len(active) == 0:
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
        with open(os.path.join(output_folder, reg.match(csv_file).group() + '.csv'), 'a') as outfile:
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

    if len(sys.argv) is 1:
        scrap(zip_dir, False)
        extract(zip_dir, raw_dir, False)
        merge(raw_dir, out_dir)
    if len(sys.argv) is 2:
        if 's' in sys.argv[1]:
            scrap(zip_dir, 'f' in sys.argv[1])
        if 'e' in sys.argv[1]:
            extract(zip_dir, raw_dir, 'f' in sys.argv[1])
        if 'm' in sys.argv[1]:
            merge(raw_dir, out_dir)


if __name__ == '__main__':
    main()
