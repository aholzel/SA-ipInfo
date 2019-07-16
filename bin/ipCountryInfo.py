#!/usr/bin/env python

import os.path
import csv
import sys
import geoip2.database


""" An adapter that takes an ip as input and produces country data
    based on the max mind data sets

"""

module_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.abspath(os.path.join(module_dir, os.pardir))
data_path = os.path.join(app_dir,'data')

def main():

    ipfield = sys.argv[1]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    header = r.fieldnames

    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:

      try:
        country2_file = os.path.join(data_path,'GeoIP2-Country.mmdb')
        country2lite_file = os.path.join(data_path,'GeoLite2-Country.mmdb')
        if (os.path.isfile(country2_file)):
                countryreader = geoip2.database.Reader(country2_file)
        elif (os.path.isfile(city2lite_file)):
                countryreader = geoip2.database.Reader(country2lite_file)

        if not countryreader is None:
          country_response = countryreader.country(result[ipfield])
          result['continent'] = country_response.continent.name
          result['country'] = country_response.country.name
          result['registered_country'] = country_response.registered_country.name
          result['represented_country'] = country_response.represented_country.name
      except geoip2.errors.AddressNotFoundError:
          donothing=""

      try:
        city2_file = os.path.join(data_path,'GeoIP2-City.mmdb')
        city2lite_file = os.path.join(data_path,'GeoLite2-City.mmdb')
        if (os.path.isfile(city2_file)):
                city2reader = geoip2.database.Reader(city2_file)
        elif (os.path.isfile(city2lite_file)):
                city2reader = geoip2.database.Reader(city2lite_file)

        if not city2reader is None:
          city2response = city2reader.city(result[ipfield])
          result['accuracy_radius'] = city2response.location.accuracy_radius
          result['city'] = city2response.city.name
          result['lat'] = city2response.location.latitude
          result['long'] = city2response.location.longitude
      except geoip2.errors.AddressNotFoundError:
        donothing=""

      w.writerow(result)

main()
