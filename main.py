import scr2

with open('ufr_offense_small.txt') as ufrs:
    for i, url in enumerate(ufrs):
        url = url.replace('\n','')
        # print(url)
        scr2.runs(url)