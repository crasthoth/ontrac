#! python3
# ontrac.py - Checks ontrac shipping website for tracking updates.
import sys
from time import sleep
from bs4 import BeautifulSoup

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

# TODO: Compare Status
def sendUpdates(tracknums,status,tophone='+13608272736'):
    account_sid = 'ACba0b39393ba93b85fd80874bb1893e0c'
    auth_token = '5567606e1eb40029c030d53f251bf7eb'
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body = "-\nPackage Update\nOnTrac Number: {}\nStatus: {}".format(tracknums,status),
                        from_ = '+13603472944',
                        to = tophone
                    )
    #print(message.sid)
    return

cont = True
while cont:
    sleep(2)
    if 'status' in locals():
        oldstatus = status
    else:
        oldstatus = ''
    status = getStatus(tracknums)
    if status != oldstatus:
        print("UPDATE: {}".format(status))
        sendUpdates(tracknums,status)
        if status == 'Delivered':
            kill = False
            print("Delivered, exiting...")
            exit()
