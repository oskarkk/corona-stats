#!/usr/bin/python -i

import requests, datetime, json, itertools
from flag import flag # flag('us')
from prettyprinter import cpprint
from copy import deepcopy

import scrapper

emoji = {'virus': '🦠', 'skull': '💀', 'ok':'✅', 'world': '🌍', 'testtube': '🧪'}
cases_url = 'https://corona-stats.online/?format=json&source=2'

# merging AND cleaning things in <cases>
def merge_cases_and_tests(cases, tests):
    stats = deepcopy(cases)

    # remove countries which aren't countries (e.g. Diamond Princess)
    # maybe it would be better to find one contry and just del it
    stats['data'] = [ x for x in stats['data'] if x['countryInfo']['_id'] ]

    # in the json from corona-stats.online sometimes there is null
    # where should just be 0
    for country in stats['data']:
        for x in ('cases', 'deaths', 'todayCases', 'todayDeaths'):
            if country[x] == None:
                # give a warning just in case
                print(country, '\nchanging None to 0')
                country[x] = 0

    for country_s in stats['data']:
        for country_t in tests:
            if country_s['country'] == country_t['country']:
                country_s['tests'] = deepcopy(country_t)
                del country_s['tests']['country']
    return stats

# new / (total - new)
def ratio(new, total):
    denom = total - new
    return round(new / denom, 3) if denom else None

def add_ratios(data):
    for c in itertools.chain(data['data'], [data['worldStats']]):
        c['todayCasesRatio'] = ratio(c['todayCases'], c['cases'])
        c['todayDeathsRatio'] = ratio(c['todayDeaths'], c['deaths'])
        c['fatalityRate'] = round(c['deaths'] / c['cases'] \
                                  if c['cases'] else None, 3)

# replace links to pics by emoji flags
def add_flags(data):
    for country in data['data']:
        country['countryInfo']['flag'] = flag(country['countryInfo']['iso2'])
    return

def save(data, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

def load(filename):
    with open(filename, 'r') as f:
        return f.read()

def countries(data, sort='cases', rev=1, max=None):
    data['data'].sort(key=lambda x: x[sort], reverse=rev)
    return data['data'][:max]

def world(data):
    return data['worldStats']

# name mess but it works
def country(data, name):
    for country in data['data']:
        if country['country'] == name:
            return country

def pretty(x):
    return cpprint(x, indent=2)

def polska(data):
    for x in stats['data']:
        if x['countryInfo']['iso2'] == 'PL':
            return x

# poland new, poland total, world total
# TODO: world top
def summary(filename=None, max=5):
    pl = polska(stats)
    w = stats['worldStats']
    date = datetime.datetime.strptime(pl['tests']['date'],'%Y-%m-%d')
    if date.date() == datetime.date.today():
        weekday = 'dziś'
    else:
        weekdays = ['niedzielę', 'poniedziałek', 'wtorek', 'środę',
                    'czwartek', 'piątek', 'sobotę']
        weekday = 'w ' + weekdays[int(date.strftime('%w'))]

    s = [
        emoji['virus'], pl['todayCases'], '/',
        emoji['skull'], pl['todayDeaths'], '\n\n',

        pl['countryInfo']['flag']+'  ',
        emoji['virus'], pl['cases'], '/',
        emoji['skull'], pl['deaths'], '/',
        emoji['ok'], pl['recovered'], '/',
        emoji['testtube'], nums(pl['tests']['tests']),
        '\n(liczba testów aktualizowana', weekday+')\n\n',

        emoji['world']+'  ',
        emoji['virus'], nums(w['cases']), '/',
        emoji['skull'], nums(w['deaths']), '/',
        emoji['ok'], nums(w['recovered'])
    ]
    
    if filename:
        with open(filename, 'w') as f:
            print(*s, file=f)
    
    print(*s)

def nums(x):
    if x < 951:
        return str(round(x,-2))
    elif x < 1000000:
        return str(round(x,-3))[:-3]+'k'
    else:
        s = str(round(x,-3))[:-5]
        return s[:-1] + ',' + s[-1:] + 'M'

if __name__ == '__main__':
    cases = requests.get(cases_url).json()
    tests = scrapper.tests()
    stats = merge_cases_and_tests(cases, tests)
    add_flags(stats)
    add_ratios(stats)
