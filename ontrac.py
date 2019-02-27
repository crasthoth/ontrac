#! python3
# ontrac.py - Checks ontrac shipping website for tracking updates, then sends via sms.
import sys
from time import sleep
from bs4 import BeautifulSoup
import local_settings

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# Only needed for requests module page fetching
#import requests

# Only needed for selenium page fetching. also requires PhantomJS
from selenium import webdriver

tracknums = ','.join(sys.argv[1:])

# Abandoned code since requests was getting a loading page, probably JS issue.
# Much faster, Will implement in the future if a way is discovered
#res = requests.get(url)
#res.raise_for_status()
#soup = bs4.BeautifulSoup(res.text, 'lxml')



# Retrieve status
# TODO: multithread check each item in the list
def getStatus(tracknums):
    url = 'https://amway.narvar.com/amway/tracking/ontrac?tracking_numbers={}&locale=en_US'.format(tracknums)
    browser = webdriver.PhantomJS()
    #print("Fetching {}".format(url))
    browser.get(url)
    html = browser.page_source
    #print("Parsing page")
    soup = BeautifulSoup(html, 'lxml')
    trackElem = soup.select('tracking-status h2')[0].text
    #print("Status: {}".format(trackElem))
    return trackElem

def sendUpdates(tracknums,status,tophone = local_settings.phone):

    #account_sid = 'your_sid'
    #auth_token = 'your_token'

    # Import credentials from credentials.py library 'auth'
    account_sid = local_settings.twilioauth['account_sid']
    auth_token = local_settings.twilioauth['auth_token']

    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body = "-\nPackage Update\nOnTrac Number: {}\nStatus: {}".format(tracknums,status),
                        from_ = '+13603472944',
                        to = tophone
                    )
    #print(message.sid)
    return

c = True
while c:
    # TIMER BLOCK - to vary the time between server requests
    t = 0
    #from random import randint
    #t = randint(0,60)
    #print('Sleeping {} + x seconds.'.format(t))
    sleep(t + 30) # this sleep to pause between requests
    if 'status' in locals():
        oldstatus = status
    else:
        oldstatus = ''
    status = getStatus(tracknums)
    if status != oldstatus:
        print("UPDATE: {}".format(status))
        sendUpdates(tracknums,status)
        if status == 'Delivered':
            c = False
            print("Delivered, exiting...")
            exit()
