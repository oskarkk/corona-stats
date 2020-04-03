import requests
from flag import flag # flag('us')
#import emoji
from prettyprinter import cpprint
from bs4 import BeautifulSoup


stats_url = 'https://corona-stats.online/?format=json&source=2'
tests_url = 'https://en.wikipedia.org/wiki/Template:COVID-19_testing'

resp = requests.get(stats_url).json()

def save(data, filename):
    with open(filename, 'w') as f:
        f.write(str(data))

def countries(data, sort='cases', max=15):
    data['data'].sort(key=lambda x: x[sort], reverse=1)
    return data['data'][:max]

def world(data):
    return data['worldStats']

def pretty(x):
    return cpprint(x, indent=2)

def polska():
    return

def tests():
    html = requests.get(tests_url).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select('table.wikitable.sortable')
    countries = table[0].tbody.find_all('tr')[1:]

    headers = ['country', 'tests', 'positive', 'date',
        'tests_per_million_people', 'positive_per_thousand_tests']

    data = []
    for country in countries:
        cells = country(['th','td'])
        # nie zadziała bo nie każda komórka ma zawartość
        #stats = dict(zip( headers, [next(x.stripped_strings) for x in cells] ))
        values = [cell.get_text().strip() for cell in cells]
        stats = dict(zip(headers, values))
        # nie zadziała bo nie w każdym wierszu jest ten atrybut daty
        # stats['date'] = cells[3].span['data-sort-value']

        # remove regions of countries
        if ':' in stats['country']:
            continue
        data.append(stats)

    return data
