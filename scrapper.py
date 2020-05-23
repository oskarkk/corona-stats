from bs4 import BeautifulSoup
import requests, datetime, json


table_url = 'https://en.wikipedia.org/wiki/Template:COVID-19_testing'

# column names
#headers = ('country', 'tests', 'positive', 'date',
#    'tests_per_M_people', 'positive_per_k_tests')
headers = (
    'country', 'date', 'tests', 'tests_units', 'positive',
    'positive_ratio', 'tests_per_M_people', 'positive_per_k_tests'
)

# 'name from wikipedia table or cases table': 'better name'
name_map = {
    'United States (unofficial)': 'USA',
    'United Kingdom': 'UK',
    'S. Korea': 'South Korea',
    'Palestinian Territory, Occupied': 'Palestine',
    'North Macedonia': 'Macedonia',
    'Bosnia': 'Bosnia and Herzegovina',
    'UAE': 'United Arab Emirates',
    'Holy See (Vatican City State)': 'Vatican',
    'Tanzania, United Republic of': 'Tanzania',
    'Moldova, Republic of': 'Moldova',
    'Syrian Arab Republic': 'Syria',
    'Libyan Arab Jamahiriya': 'Libia'
}

# remove unneeded characters etc
# U+202C POP DIRECTIONAL FORMATTING - PDF character only
# ^ this rather shouldn't be here and probably someone just copied it
# with the number from somewhere
def clean(s):
    dirt = ['\u202c']
    for d in dirt:
        s = s.replace(d, '')
    return s

# scrapper for table from wikipedia with coronavirus tests by country
def tests():
    html = requests.get(table_url).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select('table.wikitable.sortable')
    countries = table[0].tbody.find_all('tr')[1:]

    data = []

    for country in countries:
        cells = country(['th','td'])
        values = [clean(cell.get_text().strip()) for cell in cells]
        stats = dict(zip(headers, values))
        name = stats['country']

        # remove regions of countries
        # now it doesn't do nothing as there are no colons, but whatever
        if ':' in name:
            continue

        # solve differences between countries names in sources
        # maybe it can be simplified?
        if stats['country'] in name_map:
            stats['country'] = name_map[stats['country']]

        # remove empty values
        # they're sometimes adding * after number so remove it
        stats = {k: v.replace('*','') for k, v in stats.items() if v != ''}
        # change vals to ints
        for stat in ['tests', 'positive']:
            if stat in stats:
                # almost always they separate thousands with ','
                # but sometimes '.'
                stats[stat] = int(stats[stat].replace(',','').replace('.',''))
        # change vals that sometimes are floats to floats
        for stat in ['tests_per_M_people', 'positive_per_k_tests']:
            if stat in stats:
                stats[stat] = float(stats[stat].replace(',',''))

        if 'positive_ratio' in stats:
            stats['positive_ratio'] = float(stats['positive_ratio']) / 100

        # Earlier, they didn't have China in the list, they only had China's
        # provinces. Now there is an empty "China" row (only country name),
        # so let's just remove everything that doesn't have a date
        # (that's where an exception was thrown in code below).
        if not 'date' in stats: continue

        # change dates from something like "2 Apr" to yyyy-mm-dd
        # span['data-sort-value'] won't work cos date attr isn't in every row
        # UPDATE 2020-04-26: they changed it to format like "2 April",
        # but not everywhere, so we need to try to do it both ways
        try:
            date = datetime.datetime.strptime(stats['date'],'%d %B')
        except ValueError:
            date = datetime.datetime.strptime(stats['date'],'%d %b')
        
        # it won't work next year
        stats['date'] = date.replace(year=2020).strftime('%Y-%m-%d')

        data.append(stats)

    return data


# to test differences betwwen names on corona-stats.online and wikipedia table
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
