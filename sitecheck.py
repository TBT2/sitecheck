#!/usr/bin/env python

# RIVIAM Digital Care - internal site checker

"""
This script is designed to check websites that are not internet facing and therefore can't be checked
by thridparty services.

The log files will then be used to trigger if there is a problem to provide downtime stats

"""


import pickle, os, sys, logging
import httplib2
from datetime import datetime

def get_site_status(url):
    """
    Attempt to get a connection to the site.
    :param url: full URL to check
    :return: up / down
    """
    repCode=None

    if url is "":
        return("Not Valid")

    try:
        t1 = datetime.now()
        response = get_response(url)
        t2 = datetime.now()

        elapsed = t2-t1

        retTime = elapsed.microseconds

        repCode = getattr(response, 'status')

        logResponse(url,repCode,"",str(retTime))

        if repCode == 200:
            return 'up'
    except Exception as e:
        logResponse(url,repCode,e)
        pass
    return 'down'

def logResponse(url=None,respCode=None,error=None,elapsed=None):
    """
    Log out to file
    :param url: the called URL
    :param respCode: HTTP response code
    :param error: optional error string
    :return:
    """
    if respCode <> 200:
        logging.error('URL: %s, Response: %s, Error: %s, Elapsed: %s' % (url, respCode, error,elapsed))
    else:
        logging.info('URL: %s, Response: %s, OK: %s, Elapsed: %s' % (url, respCode,error,elapsed))

def get_response(url):
    """
    Check the URL
    :param url: full URI
    :return: connection object
    """

    conn = httplib2.Http(ca_certs="/etc/ssl/certs/ca-bundle.crt",disable_ssl_certificate_validation=True)
    return conn.request(url)[0]

def main(urls,logfileLocation):
    # Setup logging to store time
    logging.basicConfig(level=logging.DEBUG,
                        filename=logfileLocation,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    map(get_site_status,urls)

if __name__ == '__main__':
    # First argument needs to be a file with a list of URIs
    # Second the logfile to use
    try:
        if sys.argv[1:]:
            with open(sys.argv[1],"r") as inFile:
                data = inFile.read().split('\n')

            if len(sys.argv) > 2:
                main(data,sys.argv[2])
            else:
                print("Need to have a logfile location")
        else:
            print("call with a text file of URLs and the logfile path")
    except Exception as e:
        print("Failed with error %s" % e)
