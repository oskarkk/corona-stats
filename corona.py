import requests
from flag import flag
#import emoji
from prettyprinter import cpprint


stats_url = 'https://corona-stats.online/?format=json&source=2'
resp = requests.get(stats_url).json()

def save(data, filename):
    with open(filename, 'w') as f:
        f.write(data)

def countries(data, sort='cases', max=15):
    data['data'].sort(key=lambda x: x[sort], reverse=1)
    return data['data'][:max]

def world(data):
    return data['worldStats']

def pretty(x):
    return cpprint(x, indent=2)
