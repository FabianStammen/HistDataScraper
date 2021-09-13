"""HistoricDataScraper Util
A script that transforms the historic forex form one minute data to five minute data and some additional cleanup
of data that is not consecutive for at least 5 minutes.
"""
import csv
import os
from collections import deque


def clean_list_deque(list_deque):
    for full_list in list_deque:
        full_list.clear()


if __name__ == '__main__':
    root_dir = os.getcwd()
    data_dir = os.path.join(root_dir, 'data')
    forex_1m_dir = os.path.join(data_dir, 'Forex-1M')
    forex_5m_dir = os.path.join(data_dir, 'Forex-5M')
    try:
        os.makedirs(forex_5m_dir)
    except FileExistsError:
        for old_file in os.listdir(forex_5m_dir):
            os.remove(os.path.join(forex_5m_dir, old_file))
    csv_files = sorted(os.listdir(forex_1m_dir))
    csv_count = len(csv_files)
    for index_i, file in enumerate(csv_files):
        original_file = os.path.join(forex_1m_dir, file)
        new_file = os.path.join(forex_5m_dir, file.replace('M1', 'M5'))
        last_rows = deque(5 * [[]], maxlen=5)
        with open(original_file, 'r') as read_obj, open(new_file, 'w', newline='') as write_obj:
            reader = csv.reader(read_obj, delimiter=',')
            writer = csv.writer(write_obj, delimiter=',')
            hist_count = len(list(reader))
            read_obj.seek(0)
            for index_j, row in enumerate(reader):
                if last_rows[-1]:
                    delta_m = int(row[1]) - int(last_rows[-1][1])
                    if delta_m == 1:
                        last_rows.append(row)
                    else:
                        clean_list_deque(last_rows)
                        continue
                    if last_rows[0]:
                        high = 0
                        low = 0
                        for saved_row in last_rows:
                            if float(saved_row[3]) < 0 or float(saved_row[4]) < 0:
                                print('negative bid detected')
                            if float(saved_row[3]) > high:
                                high = float(saved_row[3])
                            if float(saved_row[4]) > low:
                                low = float(saved_row[4])
                        condensed_row = [last_rows[0][0], last_rows[0][1], last_rows[0][2], str(high), str(low),
                                         last_rows[4][5]]
                        writer.writerow(condensed_row)
                        clean_list_deque(last_rows)
                else:
                    last_rows.append(row)
                print('\r' + ' Processing: Row '
                      + str(index_j + 1).zfill(len(str(hist_count)))
                      + '/' + str(hist_count) + ' of CSV-File '
                      + str(index_i + 1).zfill(len(str(csv_count)))
                      + '/' + str(csv_count) + ' : ' + file,
                      end='', flush=True)
