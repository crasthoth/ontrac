#! python3
# ontrac.py - Checks ontrac shipping website for tracking updates, then sends via sms.
import sys, os
from time import sleep # only needed to add delay between server requests
import local_settings # library of personal info that is .gitignore

# BeautifulSoup is only needed for parsing and HTML response
#from bs4 import BeautifulSoup

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# Only needed for requests module page fetching
import requests

# Only needed for selenium page fetching. also requires PhantomJS
#from selenium import webdriver

# for parsing JSON
import json

# --------------END DEPENDENCIES--------------

# TODO: change this to come in as a list and multithread will break it apart and try each tracking number individually
# TODO: figure out how the json return happens for multiple tracking numbers
# TODO: Implement error return when no tracking number provided
if len(sys.argv) > 1:
    tracknums = ','.join(sys.argv[1:])
else:
    sys.exit("No tracking number provided")
# Much faster, trying to parse immediate json response instead of using PhantomJS
# TODO: send requests to https://amway.narvar.com/trackinginfo/amway/ontrac?tracking_numbers=C000000000
def requeststatus(tracknums):
    url = 'https://amway.narvar.com/amway/trackinginfo/ontrac?tracking_numbers={}'.format(tracknums)

    res = requests.get(url)
    res.raise_for_status()
    parsed_json = json.loads(res.text)
    #print(parsed_json)
    return parsed_json['status']

# PhantomJS handler deprecated with JSON requests; html parsing not necessary
# def phantomgetstatus(tracknums):
#     #url = 'https://amway.narvar.com/amway/tracking/ontrac?tracking_numbers={}&locale=en_US'.format(tracknums)
#     url = 'https://amway.narvar.com/amway/trackinginfo/ontrac?tracking_numbers={}'.format(tracknums)
#     browser = webdriver.PhantomJS()
#     print("Fetching {}".format(url))
#     browser.get(url)
#     html = browser.page_source
#     #print("Parsing page")
#     soup = BeautifulSoup(html, 'lxml')
#     trackstatus = soup.select('tracking-status h2')[0].text
#     #print("Status: {}".format(trackstatus))
#     return trackstatus

# TODO: multithread check each item in the tracking num list
def sendupdates(message,tophone = local_settings.tophone, fromphone = local_settings.fromphone):
    account_sid = local_settings.twilioauth['account_sid']
    auth_token = local_settings.twilioauth['auth_token']
    client = Client(account_sid, auth_token)

    sendmessage = client.messages \
    .create(
        body = message,
        from_ = fromphone,
        to = tophone
    )
    #print(message.sid)
    return

c = True
while c:
    if 'status' in locals():
        oldstatus = status
    else:
        oldstatus = ''
        status = requeststatus(tracknums)
    if status != oldstatus:
        print("UPDATE: {}".format(status))
        print("Sending update to {}".format(local_settings.tophone))
        message = "-\nPackage Update\nOnTrac Number: {}\nStatus: {}".format(tracknums,status)
        #print("Simulate message send: {}".format(message)) # for testing without sending yourself lots of messages
        sendupdates(message) # comment out to skip sending sms
    if status == 'Delivered':
        c = False
        try:
            os.remove('ghostdriver.log')
        except:
            pass
        #sys.stdout.flush() # doesn't do anything
        print("Delivered, exiting...")
    else:
        # TIMER BLOCK - to vary the time between server requests
        print('Sleeping...')
        #from random import randint
        #sleep(randint(0,120))
        sleep(local_settings.delay) # this sleep to pause between requests
