#!/usr/bin/python3 -i

import requests, datetime, json, itertools
from flag import flag # flag('us')
from prettyprinter import cpprint
from pathlib import Path

from scrapper import name_map

emoji = {'virus': '🦠', 'skull': '💀', 'ok':'✅', 'world': '🌍', 'test': '🧪'}
cases_url = 'https://corona-stats.online/?format=json&source=2'

Path('data').mkdir(exist_ok=True)

class Stats:
    def __init__(self, cases=None, from_json=None):
        if from_json:
            self.countries = from_json['countries']
            self.world = from_json['world']
            self.add_europe()
        else:
            # add countries which have id, which excludes e.g. Diamond Princess
            self.countries = [x for x in cases['data'] if x['countryInfo']['_id']]

            self.world = cases['worldStats']
            self.add_more_info()
            self.add_europe()

    def add_more_info(self):
        for country in self.countries:
            name = country['country']
            iso_code = country['countryInfo']['iso2']

            # make names better
            if name in name_map:
                country['country'] = name_map[name]

            # in the json from corona-stats.online sometimes there is null
            # where should just be 0
            for x in ('cases', 'deaths', 'todayCases', 'todayDeaths'):
                if country[x] == None:
                    # give a warning just in case
                    print(country, '\nchanging None to 0')
                    country[x] = 0

            # replace links to pics by emoji flags
            country['countryInfo']['flag'] = flag(iso_code)

            self.add_ratios(country)
        
        self.add_ratios(self.world)

    @classmethod
    def load(cls, filename=None):
        if not filename:
            filename = max(Path('./data').glob('stats-*.json'))
        
        with open(filename, 'r') as f:
            string = json.loads(f.read())
            return cls(from_json=string)

    def save(self, filename=None):
        if not filename:
            t = now()
            filename = 'data/stats-' + t + '.json'
        
        with open(filename, 'w') as f:
            dic = {'countries': self.countries, 'world': self.world}
            f.write(json.dumps(dic))

    def add_europe(self):
        self.europe = []

        with open('europe.txt', 'r') as f:
            european = f.read().splitlines()

        for country in self.countries:
            # find european countries
            if country['country'] in european:
                self.europe.append(country)

    # add some useful missing indicators 
    @staticmethod
    def add_ratios(c):
        c['recoveredRatio'] = round(c['recovered'] / c['cases'] \
                                    if c['cases'] else None, 3)
        c['todayCasesRatio'] = ratio(c['todayCases'], c['cases'])
        c['todayDeathsRatio'] = ratio(c['todayDeaths'], c['deaths'])
        c['fatalityRate'] = round(c['deaths'] / c['cases'] \
                                  if c['cases'] else None, 3)

    # name mess but it works
    def country(self, name):
        for country in self.countries:
            if country['country'] == name:
                return country

    def top(self, sort='cases', rev=1, max=None):
        top = sorted(self.countries, key=lambda x: x[sort], reverse=rev)
        return top[:max]

    def poland(self):
        return self.country('Poland')

def now():
    return datetime.datetime.today().strftime('%Y-%m-%d--%H-%M-%S')

# new / (total - new)
def ratio(new, total):
    denom = total - new
    return round(new / denom, 3) if denom else None

def pretty(x):
    return cpprint(x, indent=2)

# poland new, poland total, world total
# TODO: world top
def summary(data, filename=None, max=5):
    pl = stats.poland()
    w = stats.world

    s = [
        emoji['virus'], pl['todayCases'], '/',
        emoji['skull'], pl['todayDeaths'], '\n\n',

        pl['countryInfo']['flag']+'  ',
        emoji['virus'], nums(pl['cases']), '/',
        emoji['skull'], pl['deaths'], '/',
        emoji['ok'], nums(pl['recovered']),
        '(' + str(round(pl['recoveredRatio']*100, 1)) + '%)', '/',
        emoji['test'], nums(pl['tests']),

        '\nNa milion:',
        emoji['virus'], pl['casesPerOneMillion'], '/',
        emoji['skull'], pl['deathsPerOneMillion'], '/',
        emoji['test'], nums(pl['testsPerOneMillion']),

        '\nŚmiertelność:', str(round(pl['fatalityRate']*100, 1)) + '%\n\n',

        emoji['world']+'  ',
        emoji['virus'], nums(w['cases']), '/',
        emoji['skull'], nums(w['deaths']), '/',
        emoji['ok'], nums(w['recovered'])
    ]
    
    if filename != 0:
        if not filename:
            t = now()
            filename = 'data/summary-' + t + '.txt'
        with open(filename, 'w') as f:
            print(*s, file=f)
    
    print(*s)

def nums(x):
    if x < 951:
        return str(round(x,-2))
    elif x < 1000000:
        return str(round(x,-3))[:-3]+'k'
    else:
        s = str(round(x,-5))[:-5]
        return s[:-1] + ',' + s[-1:] + 'M'

if __name__ == '__main__':
    cases = requests.get(cases_url).json()
    stats = Stats(cases)