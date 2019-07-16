#!/usr/bin/env python

import urllib, urllib2       # to open/download the files
import os, re                # to test if a path exists and to delete the tmp files
from shutil import copyfile  # to copy the downloaded file from the tmp dir to the production location
import gzip                  # to unzip the downloaded file
import hashlib               # to get hashes from files and other content
import datetime              # to create a time stamp for log rows.

# Some static parameters for the script.
app_dir                    = os.path.dirname(os.path.abspath(__file__))[0:-3]  # Get the full path for the app
license_file               = app_dir + 'bin/GeoIP.conf'                        # this is the file with the config to download the databases
update_host                = 'updates.maxmind.com'                             # domain to download from
proto                      = 'http'                                            # protocol to us

## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
## !! Please note: 
## !!   changing the "dest_dir" and/or "city_file_dest_name" variables also means that you need to manualy change the limits.conf file
dest_dir                   = app_dir + 'data/'                                 # destination for the database file
city_file_dest_name        = 'GeoCity.mmdb'                                    # destination file name for the city database, both free and payed will get the same destination name for config simplicity
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

tmp_dir                    = app_dir + 'tmp/'                                  # temp dir to download to
log_file                   = app_dir + 'log/downloads.log'                     # logfile to write to
log_level                  = 1                                                 # log level to use 0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR
use_proxy                  = 0                                                 # Use a proxy server to connect to the internet
proxy_server               = "123.123.123.123"                                 # IP or DNS name of the proxy server
proxy_port                 = 8080                                              # proxy port
proxy_protocol             = "http"                                            # protocol to connect to the proxy server

###################################################
###    Connect to the proxy server if needed    ###
###################################################
if use_proxy == 1:
  proxy_connection         = urllib2.ProxyHandler({proxy_protocol : str(proxy_server) + ":" + str(proxy_port)})
  open_proxy_connection    = urllib2.build_opener(proxy_connection)
  urllib2.install_opener(open_proxy_connection)

###################################################
###           Start of the functions            ###
###################################################
###################################################
###  Function to check for internet connection  ###
###################################################
def Check_Internet_Connection(check_url):
    try:
        response        = urllib2.urlopen(check_url, timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False
	
###################################################
###      Function to write text to logfile      ###
###################################################
def Write_to_log( text, text_log_level=1 ):
  # 0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR
  if text_log_level >= log_level:
    if text_log_level == 0:
      text_log_level = 'DEBUG'
    elif text_log_level == 1:
      text_log_level = 'INFO'
    elif text_log_level == 2:
      text_log_level = 'WARNING'
    elif text_log_level == 3:
      text_log_level = 'ERROR'
	  
    log_line               = datetime.datetime.now().isoformat() + ", " + text_log_level + ", " + text + '\n'
  
    with open(log_file, 'a') as logfile:
      logfile.write(log_line)

###################################################
### Function to delete the temp download files  ###
###################################################
def Delete_Files( directory, pattern ):
  for file in os.listdir(directory):
    if file.endswith(pattern):
      os.remove(os.path.join(directory, file))

###################################################
###     Function to download the databases      ###
###################################################
def GeoIP_update_database_general( user_id, license_key, product_id ):
  Write_to_log('Start check if there is a new database file, product_id="' + product_id + '"')
  
  # Get the filename from the productID that we want to download
  url_getfilename          = proto + '://' + update_host + '/app/update_getfilename'
  Write_to_log('Base URL to get the name of the file, url_getfilename="' + url_getfilename + '"', 0)
  
  # create a list with variables to pass to the url, urlencode them, and create a new (complete) url to use
  values_getfilename       = { }
  values_getfilename['product_id'] = product_id
  url_getfilename_values   = urllib.urlencode(values_getfilename)
  full_url                 = url_getfilename + '?' + url_getfilename_values
  Write_to_log('URL with added variables, full_url="' + full_url + '"', 0)
  
  # This is the first URL that we try to open/connect to. So first we check if we have a internet connection to the update server
  # if not we report that in the log file and quit the script.
  test_connection        = Check_Internet_Connection(full_url)
  
  if test_connection == False:
    Write_to_log('There is no internet connection or at least no connection to ' + proto + '://' + update_host + ', exit the script', 3)
    quit()
    
  response_getfilename     = urllib2.urlopen(full_url)
  db_filename              = response_getfilename.read()
  
  Write_to_log('Filename of the file to download, db_filename="' + db_filename + '"', 0)
  
  # Check the filename that needs to be used, in case of an City database use the "city_file_dest_name"
  if db_filename.find('City') >= 0:
    check_filename         = city_file_dest_name
  else:
    check_filename         = db_filename

  # Get the md5 hash from the current file
  if os.path.exists(dest_dir + check_filename):
    old_md5                = hashlib.md5(open(dest_dir + check_filename, 'rb').read()).hexdigest()
    Write_to_log(check_filename + ' File already exists md5 hash of the file, old_md5="' + old_md5 + '"')
  else:
    old_md5                = '00000000000000000000000000000000'
    Write_to_log(check_filename + ' File doesn\'t exists set default md5 hash, old_md5="' + old_md5 + '"', 2)
  
  # Get the client ip address from the MaxMind site
  url_client_ip            = proto + '://' + update_host + '/app/update_getipaddr'
  Write_to_log('URL to get the client IP from the maxmind site, url_client_ip="' + url_client_ip + '"', 0)
  response_client_ip       = urllib2.urlopen(url_client_ip)
  client_ip                = response_client_ip.read()
  Write_to_log('Maxmind response, client_ip="' + client_ip + '"', 0)
  
  # create an md5 hash of the license key and the clientip to use as challenge
  key_and_ip               = license_key + client_ip
  challenge_md5            = hashlib.md5(key_and_ip).hexdigest()
  Write_to_log('Concatenate the license key and the client ip and get an md5 hash of that, challenge_md5="' + challenge_md5 + '"', 0)
  
  # Download the new database file
  url_getDB                = proto + '://' + update_host + '/app/update_secure'
  Write_to_log('URL to get the database file, url_getfilename="' + url_getDB + '"', 0)
  
  values_getDB             = { }
  values_getDB['db_md5']        = old_md5
  values_getDB['challenge_md5'] = challenge_md5
  values_getDB['user_id']       = user_id
  values_getDB['edition_id']    = product_id
  Write_to_log('Variables to pass to the URL, db_md5="' + old_md5 + '", challenge_md5="' + challenge_md5 +'", user_id="' + user_id +'", edition_id="' + product_id +'"', 0)
  
  url_getDB_values         = urllib.urlencode(values_getDB)
  full_url_getDB           = url_getDB + '?' + url_getDB_values
  Write_to_log('Full URL with the URL encoded variables to download the database, full_url_getDB="' + full_url_getDB + '"', 0)
  
  response_getDB           = urllib2.urlopen(full_url_getDB)
  content_getDB            = response_getDB.read()

  content_header           = response_getDB.info().getheader('Content-Disposition')
  Write_to_log('Content header containing the filename to download, content_header="' + str(content_header) + '"', 0)

  if content_getDB.strip('\n') != 'No new updates available':
    Write_to_log('There is a new version available for download', 1)
    if content_header is None or str(content_header) == 'None':
      getDB_filename       = db_filename + '.gz'
      Write_to_log('There was no valid content header detected so we have to constuct the filename by our self, getDB_filename="' + getDB_filename + '"', 3)
    else:
      filenamepos          = content_header.find('filename=') + 9
      getDB_filename       = content_header[filenamepos::].strip()
      Write_to_log('File name to download according to the content header, getDB_filename="' + getDB_filename + '"', 1)

    Write_to_log('Start the download, unzip and move of the database file', 1)
    Write_to_log('File location and name will be: "' + tmp_dir + getDB_filename + '"', 0)
    output_getDB           = open(tmp_dir + getDB_filename, 'w+b')
    output_getDB.write(content_getDB)
    output_getDB.close()
    Write_to_log('File downloaded and written to disk in the temporary directory', 0)
    
    # Unzip and move the file from the tmp dir to the prod dir.
    Write_to_log('Start the unzipping of the downloaded file', 0)
    inFile                 = gzip.GzipFile(tmp_dir + getDB_filename, 'rb')
    content                = inFile.read()
    inFile.close()
    Write_to_log('Unzipping done in the temporary directory', 0)
	
    Write_to_log('Start the move of the database file from the temporary directory to the production directory', 0)
	Write_to_log('Production file name will be: "' + dest_dir + check_filename + '"', 0)
    outFile                = file(dest_dir + check_filename, 'w+b')
    outFile.write(content)
    outFile.close()
    Write_to_log('Done with the download, unzip and move of the database file', 1)
  else:
    Write_to_log('The version we are running is the current version no need to download', 1)
  return
  
###################################################
###            End of the functions             ###
###################################################

###################################################
###              Start the script               ###
###################################################

# read maxmind config file
if os.path.exists(license_file):
  Write_to_log('Maxmind config file found start processing', 1)
  f                        = open(license_file)
  line                     = f.readline()

  while line:
    if not line.startswith("#"):
      # convert the string to lowercase to find the lines we are looking for
      linelower            = line.lower()
      usernamePos          = linelower.find("userid")
      licenseKeyPos        = linelower.find("licensekey")
      productIdsPos        = linelower.find("productids")    

      if usernamePos >= 0:
        userIdStart        = line.find(" ")
        userId             = line[userIdStart::].strip()
        Write_to_log('Found the userId to use, userId="' + userId + '"', 0)    

      if licenseKeyPos >= 0:
        licenseKeyStart    = line.find(" ")
        licenseKey         = line[licenseKeyStart::].strip()
        Write_to_log('Found the license key to use (the following key is masked), licenseKey="' + licenseKey[0:3] + '******' + licenseKey[9::] + '"', 0 )
    
      if productIdsPos >= 0:
        productIdsStart    = line.find(" ")
        productIds         = line[productIdsStart::].strip()
        Write_to_log('Found the product ID(s) to download, productIds="' + productIds + '"', 0)
        productIds         = productIds.split()

    line = f.readline()
  f.close()
else:
  Write_to_log('Required config file is missing please create an config file named "' + license_file + '" with the required info', 3 )

if userId:
  Write_to_log('Found an userId in the config file start processing the products', 0)
  # loop through the product_ids and download the databases 
  for productId in productIds:
    Write_to_log('Start the checking of product: "' + productId + '"', 1)
    GeoIP_update_database_general( userId, licenseKey, productId )
    Write_to_log('Delete the downloaded file in the tmp directory.', 1)
    Delete_Files( tmp_dir, ".gz" )
