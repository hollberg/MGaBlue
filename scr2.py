"""scrape.py
Holds functions relating to scraping data from mgoblog.com
"""
from bs4 import BeautifulSoup  #BeautifulSoup
import lxml     #XML/HTML parser for BS
import requests
# import sqlite3
from collections import defaultdict
# from collections import namedtuple
import re
import csv


def get_soup(url):
    """Given a URL, return a BeautifulSoup tables object of all tables at the URL"""
    r = requests.get(url)
    print('URL: {0} return code: {1}{2}'.format(url, r.status_code, '/n'))
    if r.status_code != 200:  #if not valid response
        return None
    else:
        content = r.content
        return BeautifulSoup(content, 'lxml')   #Explicity use the "LXML" parsing library


def parse_table(table):
    """Pass a BeautifulSoup Table object, return a list of the rows"""
    table_list = []
    rows = table.findChildren('tr')
    for row in rows:
        if row != '\n':
            elements = row.findChildren(['td', 'th'])
            cur_row = []

            try:
                for element in elements:
                    try:
                        val = element.text
                    except:
                        val = element

                    val = re.sub('\n','', val)    # Strip hard returns
                    cur_row.append(val)
                cur_row.append(element.name)
                table_list.append(cur_row)
            except:
                pass
    return table_list


def parse_ufr_table(ufr, url):
    """pass list of UFR table rows, url source of the ufr"""

    re_ufr_data = re.compile(r'[A-Z][0-9]{1,2}')  # Start of string is like M40, I22, etc. (Starting yard marker)
    drive_num = 1
    drives = []
    current_play = []
    plays = []
    ufr_dict = defaultdict(lambda: '')
    header_row = []

    for row_num, row in enumerate(ufr):

        if row_num == 0:    # First record, write column headers
            play_num = 0
            plays.append((row, 'Note', 'drive num', 'play num', 'url'))
            header_row.append((url, row))
            csv_write('headers', [url, row])

        elif row[0][0:12] == 'Drive Notes:':    # *** END OF DRIVE ***
            play_num = 0    # Reset play counter for next drive
            drives.append((drive_num, row, url))
            drive_num += 1
        elif row[-1] == 'th':   # Then this is a repeat of row headers, skip
            pass
        elif re.match(re_ufr_data,row[0]) is not None:  #Then is a data line beginning with Yard maker (ex: M32, ie, on Michigan 32)
            play_num +=1
            current_play.append(row)
        else:   # Then it's the note for the play
            current_play.append((row[0], drive_num, play_num, url))      # Row[0] is the note, don't duplicate <tr> tag
            plays.append(current_play)
            current_play = []


    ufr_dict['plays'] = plays
    ufr_dict['drives'] = drives
    ufr_dict['header_row'] = header_row
    return ufr_dict


def csv_write(file_name, val_list):
    with open(file_name + '.csv', 'a') as csvfile:
        # fieldnames = [key for key in headers_list]
        writer = csv.writer(csvfile, delimiter = '|')
#        writer = csv.DictWriter(csvfile)
        # writer.writeheader()
        for entry in val_list:
            writer.writerow(entry)

def runs(url):
    soup = get_soup(url)
    if soup is not None:
        tables = soup.find_all('table')
        ufr_table = parse_table(tables[0])
        out = parse_ufr_table(ufr_table, url)

        for row in out['plays']:
            print(str(row))
            csv_write('plays', out['plays'])
        print('\n')
        for row in out['drives']:
            print(str(row))
        for row in out['header_row']:
            print(str(row))
            # csv_write('headers', out['header_row'])