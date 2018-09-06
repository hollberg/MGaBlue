"""Found at: https://www.reddit.com/r/scrapinghub/comments/7sqwug/data_scraping_espns_win_probabiliy/"""

from lxml import html
from lxml.cssselect import CSSSelector


import json

css = CSSSelector

win_pct_marker = "espn.gamepackage.probability.data = "


def is_wins(x):
    return win_pct_marker in x


def extract_other_wins(doc):
    scripts = css("script")(doc)
    target_script = next(script for script in scripts if is_wins(script.text_content()))
    js = target_script.text_content()
    target_line = next(line for line in js.splitlines() if is_wins(line))
    start = target_line.find(win_pct_marker)
    data = target_line[start + len(win_pct_marker):-1]
    parsed = json.loads(data)
    return parsed


def extract(src):
    doc = html.fromstring(src)
    primary_win_pct = css(".header-win-percentage")(doc)[0].text_content()
    other_win_pcts = extract_other_wins(doc)
    return (primary_win_pct, other_win_pcts)


myurl = r'http://www.espn.com/nfl/game?gameId=400927752'

print(extract(myurl))