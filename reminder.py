import requests as r
import string
from ics import Calendar
from datetime import date
import os
import logging
import google.cloud.logging

# Set up logging

client = google.cloud.logging.Client()
client.setup_logging()

# SMS Vars

acc_sid = os.environ['accsid']
acc_tkn = os.environ['acctkn']
sms_url = 'https://api.zang.io/v2/Accounts/' + acc_sid + '/SMS/Messages.json'
auth=(acc_sid,acc_tkn)

# Pickup Dict for who to send the SMS to

apt_dict = {}
apt_dict['190A'] = os.environ['nza']
apt_dict['190B'] = os.environ['nzb']
apt_dict['190C'] = os.environ['nzc']
apt_dict['190D'] = os.environ['nzd']
apt_dict['192A'] = os.environ['nta']
apt_dict['192B'] = os.environ['ntb']
apt_dict['192C'] = os.environ['ntc']
apt_dict['192D'] = os.environ['ntd']

# Get Pickup items
def getPickupItems(): 
    lookup_url = os.environ['lookup-url']
    pck_items = []
    try:
        garbage_r = r.get(lookup_url)
        garbage_r = garbage_r.json()
        pck_day = garbage_r['next_event']['day']
        year, month, day = (int(x) for x in pck_day.split('-'))
        ans = date(year, month, day)
        pck_day, pck_mth, pck_date = ans.strftime("%A"), ans.strftime("%B"), ans.strftime("%d")
        garbage_r = garbage_r['next_event']['flags']
        for item in garbage_r:
            pck_items.append(item['subject'].lower())
        return pck_items,pck_day, pck_mth, pck_date
    except garbage_r.exceptions.RequestException as e:
        logging.warn("Error recieved while getting pickup items" + e)
 

# Get next person for pickup
def getSched():
    ical_url = os.environ['ical-url']
    try:
        c = Calendar(r.get(ical_url).text)
        c.events
        next_u = list(c.timeline)[0]
        next_u = str(next_u.name)
        logging.info("Next event retrieved:" + next_u)
    except Exception as e:
        logging.warn("Error getting scheduled event")
        logging.warn(e)
    return next_u

# Get number to send SMS
def getNumber(next_u):
    if next_u in apt_dict:
        to_number = apt_dict[next_u]
    else:
        logging.warn("No number found based on event")
    return to_number

# Send Notification
def sendSms(*args):
    items = (', '.join(pck_items[:-1]) + ' and ' + pck_items[-1])
    sms_message = ("The next pickup will be on " + pck_day + ", " + pck_mth + " " + pck_date +  " and the items will be " + items + "." )
    sms_data = {"Body": sms_message, "To": to_number, "From": os.environ['sms-from']}
    try:
        sms_send = r.post(sms_url,data=sms_data,auth=auth)
        logging.info(sms_send.content)
    except sms_send.exceptions.RequestException as e:
        logging.warn("Error recieved while sending SMS" + e)

pck_items,pck_day,pck_mth, pck_date = getPickupItems()
next_u = getSched()
to_number = getNumber(next_u)
sendSms(pck_items,pck_day, pck_mth, pck_date)