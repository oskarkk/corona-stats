#!/usr/bin/python -i

import requests, datetime, json
from flag import flag # flag('us')
from prettyprinter import cpprint
from copy import deepcopy

import scrapper

cases_url = 'https://corona-stats.online/?format=json&source=2'

def merge_cases_and_tests(cases, tests):
    stats = deepcopy(cases)

    # remove countries which aren't countries (e.g. Diamond Princess)
    stats['data'] = [ x for x in stats['data'] if x['countryInfo']['_id'] ]

    for country_s in stats['data']:
        for country_t in tests:
            if country_s['country'] == country_t['country']:
                country_s['tests'] = deepcopy(country_t)
                del country_s['tests']['country']
    return stats

# replace links to pics by emoji flags
def add_flags(stats):
    for country in stats['data']:
        print(country)
        country['countryInfo']['flag'] = flag(country['countryInfo']['iso2'])
    return

def save(data, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

def countries(data, sort='cases', rev=1, max=None):
    data['data'].sort(key=lambda x: x[sort], reverse=rev)
    return data['data'][:max]

def world(data):
    return data['worldStats']

def pretty(x):
    return cpprint(x, indent=2)

def polska():
    return

if __name__ == '__main__':
    cases = requests.get(cases_url).json()
    tests = scrapper.tests()
    stats = merge_cases_and_tests(cases, tests)
    add_flags(stats)
