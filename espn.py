"""
ESPN.py
Scrape CFB data from ESPN sites
Note: ESPN game summary data URLs structured like:
    http://www.espn.com/college-football/playbyplay?gameId=400869180

"""
from collections import namedtuple
import scr2
import pandas as pd
import sqlite3
# import winprob


"""Todos
1) Map all scraped data directly to Pandas dataframe
2) Write results to SQLite DB
3) Scrape comprehensive list of Game IDs
4) Get game metadata (stadium, date, time, 
"""



# drive = namedtuple('drive', 'drive_num, team, summary, num_plays, tot_yards, time_of_pos')
drives =[]
# play = namedtuple('play', 'drive_num, play_num, clock, qtr, down, distance, location, text')
plays = []


url_prefix = 'http://www.espn.com/college-football/'
game_id = '400869180'

game_tabs = ['playbyplay',
             'boxscore',
             'matchup']


def df_from_nt(nt_list):
    """
    Dataframe from namedtuple list

    :param namedtuple: Pass a list of named tuples
    :return: Pandas dataframe with columns labeled per Named tuple elements
    """
    cols = [x for x in nt_list[0]._fields]  # List of Name Tuple element names
    data = {column: [] for column in cols}  # Dict with list per tuple element

    for entry in nt_list:
        for col in cols:
            data[col].append(getattr(entry,col))    # Get attribute of name 'col' from current entry

    return pd.DataFrame(data, columns = cols)


def espn_team_id_from_href(url):
    """Given a link to a team logo, extract the ESPN team id value
    example link: extract number "62" from below
    <img class="team-logo imageLoaded" src="http://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/62.png&amp;h=100&amp;w=100">
    """
    repl_1 = r'http://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/'
    repl_2 = r'.png&h=100&w=100'
    return str(url).replace(repl_1,'').replace(repl_2, '')

pbp_page = scr2.get_soup(url_prefix + 'playbyplay?gameId='+game_id)

pbp_block = pbp_page.find(id = 'gamepackage-drives-wrap')

drive_num = 0
play_num = 0

for element in pbp_block.recursiveChildGenerator():
    try:
        element_class = element.attrs['class']
    except:
        pass

    if element.name == 'span':
        if 'home-logo' in element_class:    # Is a new drive
            drive_num += 1
            play_num = 0    # Reset play number for new possession
            current_drive = namedtuple('current_drive', 'drive_num, team, summary, tot_yards, time_of_pos')
            logo_url = element.contents[0].attrs['src']
            current_drive.drive_num = drive_num
            current_drive.team = espn_team_id_from_href(logo_url)
        if 'headline' in element_class:
            print('Headline: ' + element.text)
            current_drive.summary = element.text
        elif 'drive-details' in element_class:
            print('Details: ' + element.text)
            current_drive.plays, current_drive.tot_yards, current_drive.time_of_pos = element.text.split(',')
            drives.append(current_drive)

    if element.name == 'li':
        if element_class == ['']:   # is a new play
            current_play = namedtuple('current_play', 'drive_num, play_num, clock, qtr, down, distance, location, text')
            play_num += 1
            current_play.play_num = play_num
            down_and_distance = element.contents[1].text.strip()    # 1st and 10 at MICH 25
            clock_and_play = element.contents[3].text.strip()       # (14:01 - 2nd) Jabill Peppers run for gain of 20 to Mich 39

            if len(down_and_distance) > 1:
                items = down_and_distance.split()
                current_play.down = items[0]
                current_play.distance = items[2]
                current_play.location = items[4] + ' ' + items[5]

                hyphen_location = clock_and_play.find('-')
                current_play.clock = clock_and_play[1:hyphen_location]
                current_play.qtr = clock_and_play[hyphen_location +2:hyphen_location + 5]
                current_play.text = clock_and_play[hyphen_location + 7:]
            else:
                current_play = ('', '', '', '', '', '', '', '', '')

            print('li: ' + element.contents[1].text.strip() + ' ' + element.contents[3].text.strip())
            plays.append(current_play)
    foo = 'bar'

print('***DRIVES***')
print(drives)

myboo = df_from_nt(drives)

print('\n****PLAYS***')
print(plays)
