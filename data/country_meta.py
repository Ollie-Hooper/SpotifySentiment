import pandas as pd

import requests
from lxml import html

url = "https://spotifycharts.com/regional"

page = requests.get(url)

tree = html.fromstring(page.text)

countries = pd.DataFrame()

countries['country'] = tree.xpath("//div[@class='responsive-select'][@data-type='country']/ul/li/@data-value")
countries['name'] = tree.xpath("//div[@class='responsive-select'][@data-type='country']/ul/li/text()")
countries.set_index('country', inplace=True)

lat_long = pd.read_csv('lat_long.csv')
lat_long['country'] = lat_long['country'].apply(lambda x: str(x).lower())
lat_long.set_index('country', inplace=True)

countries['lat'] = lat_long['latitude']
countries['long'] = lat_long['longitude']

country_iso = pd.read_csv('country_iso.csv')
country_iso['Alpha-2 code'] = country_iso['Alpha-2 code'].apply(lambda x: str(x).lower())
country_iso.set_index('Alpha-2 code', inplace=True)
countries['iso3'] = country_iso['Alpha-3 code']

countries.to_csv('country_meta.csv')
