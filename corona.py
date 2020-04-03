import requests, datetime
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

def countries(data, sort='cases', rev=1, max=None):
    data['data'].sort(key=lambda x: x[sort], reverse=rev)
    return data['data'][:max]

def world(data):
    return data['worldStats']

def pretty(x):
    return cpprint(x, indent=2)

def polska():
    return

def test_names(x,y):
    x.sort(key=lambda xx: xx['country'])
    y.sort(key=lambda xx: xx['country'])
    x.append({'country':'zzzzzzzzzzzz'})
    y.append({'country':'zzzzzzzzzzzz'})
    while len(x) or len(y):
        a = x[0]['country']
        b = y[0]['country']
        if a < b:
            print(f'{a:40.38}')
            x.pop(0)
        elif a > b:
            print(f'{"":40.38}{b}')
            y.pop(0)
        else:
            print(f'{a:40.38}{b}')
            x.pop(0)
            y.pop(0)


def tests():
    html = requests.get(tests_url).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select('table.wikitable.sortable')
    countries = table[0].tbody.find_all('tr')[1:]

    headers = ['country', 'tests', 'positive', 'date',
        'tests_per_M_people', 'positive_per_k_tests']
    name_map = {
        'United States (unofficial)': 'USA',
        'United Kingdom': 'UK',
        'South Korea': 'S. Korea',
        'Palestine': 'Palestinian Territory, Occupied',
        'North Macedonia': 'Macedonia',
        'Bosnia and Herzegovina': 'Bosnia',
        'United Arab Emirates': 'UAE'
    }

    data = []

    for country in countries:
        cells = country(['th','td'])
        # nie zadziała bo nie każda komórka ma zawartość
        #stats = dict(zip( headers, [next(x.stripped_strings) for x in cells] ))
        values = [cell.get_text().strip() for cell in cells]
        stats = dict(zip(headers, values))

        # remove regions of countries
        if ':' in stats['country']:
            continue

        # solve differences between countries names in sources
        if stats['country'] in name_map:
            stats['country'] = name_map[stats['country']]

        # remove empty values
        # they're sometimes adding * after number so remove it
        stats = {k: v.replace('*','') for k, v in stats.items() if v != ''}
        # change vals to ints
        for stat in ['tests', 'positive']:
            if stat in stats:
                stats[stat] = int(stats[stat].replace(',',''))
        # change vals that sometimes are floats to floats
        for stat in ['tests_per_M_people', 'positive_per_k_tests']:
            if stat in stats:
                stats[stat] = float(stats[stat].replace(',',''))

        # change dates from something like "2 Apr" to yyyy-mm-dd
        # span['data-sort-value'] won't work cos date attr isn't in every row
        date = datetime.datetime.strptime(stats['date'],'%d %b')
        stats['date'] = date.replace(year=2020).strftime('%Y-%m-%d')

        data.append(stats)

    return data

#for country in resp['data']:
#     if country['country'] == x[0]['country']: country
