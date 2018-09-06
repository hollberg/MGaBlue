"""scrape.py
Holds functions relating to scraping data from mgoblog.com
"""
from bs4 import BeautifulSoup  #BeautifulSoup
import lxml #XML/HTML parser for BS
import requests
import sqlite3
from collections import defaultdict
from collections import namedtuple
import re

#url = r'http://mgoblog.blogspot.com/2006/12/upon-further-review-offense-vs-osu.html'
#http://mgoblog.blogspot.com/ (June 30, 2008)
#http://mgoblog.blogspot.com/2005/09/upon-further-review-archive.html
url = r'http://mgoblog.com/content/upon-further-review-2012-offense-vs-nebraska'
#url = r'http://mgoblog.com/content/upon-further-review-2016-offense-vs-iowa'
#url = r'http://mgoblog.com/content/upon-further-review-2016-offense-vs-indiana'

def get_soup(url):
    """Given a URL, return a BeautifulSoup tables oject of all tables at the URL"""
    content = requests.get(url).content
    return BeautifulSoup(content, 'lxml')   #Explicity use the "LXML" parsing library

def parse_table(table):
    """Pass a BeautifulSoup Table object"""
    table_list = []
    rows = table.findChildren('tr')
    for row_num, row in enumerate(rows):
        if row != '\n':
            elements = row.findChildren(['td', 'th'])
            mylist = []
            try:
                for element in elements:
                #    key = str(tab_num) + '_' + str(row_num)
                    try:
                        val = element.text
                    except:
                        val = element
                    val = re.sub('\n','', val)    #Strip out all hard returns
                    mylist.append(val)
#                ufrdict[key] = mylist
                table_list.append(mylist)
            except:
                pass
    return table_list

soup = get_soup(url)
tables = soup.find_all('table')

def parse_ufr_table(ufr):
    """pass list of UFR table rows"""

    ufr_headers = ['Ln', 'Dn', 'Ds', 'O Form', 'RB', 'TE', 'WR', 'D Form', 'Box', 'Type', 'Play', 'Player', 'Yards','Note']
    re_ufr_data = re.compile(r'[A-Z][0-9]{1,2}')  # Start of string is like M40, I22, etc. (Starting yard marker)
    drive_num = 1
    drives = []
    current_play = []
    plays = []
    ufr_dict = defaultdict(lambda: '')

    for row_num, row in enumerate(ufr):
        if row_num == 0:
            play_num = 1
            plays.append(ufr_headers)

        elif row[0][0:12] == 'Drive Notes:':
            drive_num +=1
            drives.append((drive_num, row))
        elif row[0][0:2] == 'Ln':   #Then repeat of row headers
            pass
        elif re.match(re_ufr_data,row[0]) is not None:  #Then is a data line beginning with Yard maker (ex: M32, ie, on Michigan 32)
            play_num +=1
            current_play.append((row, drive_num, play_num))
        else:   #Then it's the note for the play
            current_play = current_play + row
            plays.append(current_play)
            current_play = []

    ufr_dict['plays'] = plays
    ufr_dict['drives'] = drives
    return ufr_dict


ufr_table = parse_table(tables[0])

out = parse_ufr_table(ufr_table)
#print(out['plays'])
#print(out['drives'])
for row in out['plays']:
    print(str(row))
print('\n')
for row in out['drives']:
    print(str(row))