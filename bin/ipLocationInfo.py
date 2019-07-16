#!/usr/bin/env python

import os.path
import csv
import sys
import geoip2.database


""" An adapter that takes an ip as input and produces geolocation data
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
	city2_file = os.path.join(data_path,'GeoIP2-City.mmdb')
	city2lite_file = os.path.join(data_path,'GeoLite2-City.mmdb')
	if (os.path.isfile(city2_file)):
		city2reader = geoip2.database.Reader(city2_file)
	elif (os.path.isfile(city2lite_file)):
		city2reader = geoip2.database.Reader(city2lite_file)

	if not city2reader is None:	
          city2response = city2reader.city(result[ipfield])
          result['accuracy_radius'] = city2response.location.accuracy_radius
          result['continent'] = city2response.continent.name
          result['country'] = city2response.country.name
          result['country_iso'] = city2response.country.iso_code
          result['city'] = city2response.city.name
          result['lat'] = city2response.location.latitude
          result['long'] = city2response.location.longitude
          result['postalcode'] = city2response.postal.code
          result['subdivision'] = city2response.subdivisions.most_specific.name
          result['subdivision_iso'] = city2response.subdivisions.most_specific.iso_code
          result['timezone'] = city2response.location.time_zone
      except geoip2.errors.AddressNotFoundError:
	donothing=""

      w.writerow(result)

main()
