import requests
import json
import yaml
import pymongo
import traceback
import logging
import logging.handlers
import os
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ------------- INITIALIZATION --------------------#

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['smallcap_sip_bot']

tri_collection = db['smallcap_bot_totalreturnsindex_data']
user_preferences = db['smallcap_bot_userpreferences']
user_details = db['smallcap_bot_userdetails']
alert_details = db['smallcap_bot_alerts']

# ------------- FUNCTIONS -------------------------#

def insert_alert_data(alert_details,email,status,relative_value):
    try:
        insert_data = {
            'date': datetime.today(),
            'email': email,
            'status': status,
            'relative_value': relative_value
        }
        alert_details.insert(insert_data)

        return True

    except Exception as err:
        logger.error(err,traceback.format_exc())

def fetch_data(url,headers,date_range):
    try:
        start_date,end_date = date_range

        nifty_smallcap_payload = {
            'name':'NIFTY SMLCAP 250',
            'startDate': start_date,
            'endDate': end_date
        }

        nifty_50_payload = {
            'name':'NIFTY 50',
            'startDate': start_date,
            'endDate': end_date
        }

        nifty_smallcap_payload = str(nifty_smallcap_payload)
        nifty_50_payload = str(nifty_50_payload)

        response = requests.post(url,data=nifty_smallcap_payload,headers=headers,timeout=20)
        nifty_smallcap_response = response.json()['d']

        response = requests.post(url,data=nifty_50_payload,headers=headers,timeout=20)
        nifty_50_response = response.json()['d']

        nifty_smallcap_json = json.loads(nifty_smallcap_response)
        nifty_50_json = json.loads(nifty_50_response)

        return nifty_smallcap_json, nifty_50_json

    except Exception as err:
        logger.error(traceback.format_exc())

def process_data(fetched_data,initial_values):

    nifty_smallcap_data, nifty_50_data = fetched_data
    nifty_smallcap_initial, nifty_50_initial = initial_values

    result_list =[]

    for nifty_smallcap in nifty_smallcap_data:
        tri_data = {}
        date = nifty_smallcap['Date']
        nifty_smallcap_tri = float(nifty_smallcap['TotalReturnsIndex'])

        for nifty_50 in nifty_50_data:
            if nifty_50['Date'] == date:
                nifty_50_tri = float(nifty_50['TotalReturnsIndex'])
                break

        if nifty_smallcap_tri and nifty_50_tri:
            relative_value = ((nifty_smallcap_tri / nifty_smallcap_initial) / (nifty_50_tri / nifty_50_initial))

            db_date = datetime.strptime(date, '%d %b %Y')

            tri_data['date'] = db_date
            tri_data['nifty_smallcap_tri'] = nifty_smallcap_tri
            tri_data['nifty_50_tri'] = nifty_50_tri
            tri_data['relative_value'] = relative_value

            result_list.append(tri_data)

    return result_list

def generate_alert_data(total_user_details,relative_value,threshold):

    alert_list = []

    scenario_1, scenario_2, scenario_3, scenario_4 = total_user_details

    upper_threshold, lower_threshold = threshold

    if relative_value >= upper_threshold:

        # --------- SCENARIO 1 ------------ #

        for data in scenario_1:
            scenario_1_dict = {}
            scenario_1_dict['email'] = data['email']
            scenario_1_dict['user_name'] = data['user_name']
            scenario_1_dict['subscription_option'] = data['subscription_option']
            scenario_1_dict['pause'] = True
            scenario_1_dict['purchase'] = 0
            scenario_1_dict['redeem'] = 0
            scenario_1_dict['transfer_to_nifty50'] = 0
            scenario_1_dict['note'] = "Pause SIP"

            alert_list.append(scenario_1_dict)
        
        # --------- SCENARIO 2 ------------ #

        for data in scenario_2:
            scenario_2_dict = {}
            scenario_2_dict['email'] = data['email']
            scenario_2_dict['user_name'] = data['user_name']
            scenario_2_dict['subscription_option'] = data['subscription_option']
            scenario_2_dict['pause'] = True
            scenario_2_dict['purchase'] = 0
            scenario_2_dict['redeem'] = data['sip_amount']
            scenario_2_dict['transfer_to_nifty50'] = 0
            scenario_2_dict['note'] = f"Pause SIP and Redeem {data['sip_amount']} worth of units"
                
            alert_list.append(scenario_2_dict)
        
        # --------- SCENARIO 3 ------------ #

        for data in scenario_3:
            difference = relative_value - upper_threshold
            add_value = int(difference / 0.05)
            sip_redeem_multiplier = 1 + add_value
            redeem_amount = data['sip_amount'] * sip_redeem_multiplier

            scenario_3_dict = {}
            scenario_3_dict['email'] = data['email']
            scenario_3_dict['user_name'] = data['user_name']
            scenario_3_dict['subscription_option'] = data['subscription_option']
            scenario_3_dict['pause'] = True
            scenario_3_dict['purchase'] = 0
            scenario_3_dict['redeem'] = redeem_amount
            scenario_3_dict['transfer_to_nifty50'] = 0
            scenario_3_dict['note'] = f"Pause SIP and Redeem {redeem_amount} worth of units"

            alert_list.append(scenario_3_dict)

        # --------- SCENARIO 4 ------------ #

        for data in scenario_4:
            difference = relative_value - upper_threshold
            add_value = int(difference / 0.05)
            sip_redeem_multiplier = 1 + add_value
            transfer_amount = data['sip_amount'] * sip_redeem_multiplier

            scenario_4_dict = {}
            scenario_4_dict['email'] = data['email']
            scenario_4_dict['user_name'] = data['user_name']
            scenario_4_dict['subscription_option'] = data['subscription_option']
            scenario_4_dict['pause'] = True
            scenario_4_dict['purchase'] = 0
            scenario_4_dict['redeem'] = 0
            scenario_4_dict['transfer_to_nifty50'] = transfer_amount
            scenario_4_dict['note'] = f"Pause SIP, Redeem {transfer_amount} worth of units from SmallCap Index and Buy the same in Nifty50 Index"

            alert_list.append(scenario_4_dict)
    
    else:

        # --------- SCENARIO 3 ------------ #

        for data in scenario_3:
            difference = lower_threshold - relative_value
            add_value = int(difference / 0.05)
            sip_purchase_multiplier = 1 + add_value
            purchase_amount = data['sip_amount'] + (data['sip_amount'] * sip_purchase_multiplier)

            scenario_3_dict = {}
            scenario_3_dict['email'] = data['email']
            scenario_3_dict['user_name'] = data['user_name']
            scenario_3_dict['subscription_option'] = data['subscription_option']
            scenario_3_dict['pause'] = False
            scenario_3_dict['purchase'] = purchase_amount
            scenario_3_dict['redeem'] = 0
            scenario_3_dict['transfer_to_nifty50'] = 0
            scenario_3_dict['note'] = f"Purchase {purchase_amount} worth of units"

            alert_list.append(scenario_3_dict)
        
        # --------- SCENARIO 4 ------------ #

        for data in scenario_4:
            difference = lower_threshold - relative_value
            add_value = int(difference / 0.05)
            sip_purchase_multiplier = 1 + add_value
            purchase_amount = data['sip_amount'] + (data['sip_amount'] * sip_purchase_multiplier)

            scenario_4_dict = {}
            scenario_4_dict['email'] = data['email']
            scenario_4_dict['user_name'] = data['user_name']
            scenario_4_dict['subscription_option'] = data['subscription_option']
            scenario_4_dict['pause'] = False
            scenario_4_dict['purchase'] = purchase_amount
            scenario_4_dict['redeem'] = 0
            scenario_4_dict['transfer_to_nifty50'] = 0
            scenario_4_dict['note'] = f"Purchase {purchase_amount} worth of units"

            alert_list.append(scenario_4_dict)

    return alert_list

def send_alert_mail(alert_data,relative_value):
    try:
        mail_id = os.environ.get('MAIL_ID')
        app_password = os.environ.get('APP_PASSWORD_SCRIPT')

        rounded_relative_value = str(relative_value)[:4]

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[SIP Assistant] - An alert trigger with regards to your SmallCap Investment <{rounded_relative_value}>"
        msg['From'] = "SIP Assistant"
        
        for user_data in alert_data:
            email = user_data['email']
            user_name = user_data['user_name']
            subscription_option = user_data['subscription_option']
            pause = user_data['pause']
            purchase = user_data['purchase']
            redeem = user_data['redeem']
            transfer_to_nifty50 = user_data['transfer_to_nifty50']
            note = user_data['note']
            
            recipients = [email]

            msg['To'] = "SIP Assistant"

            if subscription_option == 1:
                body_html = "Hi {0}, <br> \
                <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                <p> Currently the Relative Value is <b>{1}</b>, which is above the upper threshold. It is advisable to pause your SIP if you are planning to invest now. </p> \
                <p> <u>Alert Details:</u> </p> \
                <p> <b>Pause SIP:</b> Yes </p> \
                <p> <b>Note:</b> {2} </p> <br> \
                Thanks \
                <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,note)

            elif subscription_option == 2:
                body_html = "Hi {0}, <br> \
                <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                <p> Currently the Relative Value is <b>{1}</b>, which is above the upper threshold. It is advisable to pause your SIP and redeem some amount </p> \
                <p> <u>Alert Details:</u> </p> \
                <p> <b>Pause SIP:</b> Yes </p> \
                <p> <b>Redeem:</b> {2} </p> \
                <p> <b>Note:</b> {3} </p> <br> \
                Thanks \
                <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,redeem,note)
            
            elif subscription_option == 3:
                if pause:
                    body_html = "Hi {0}, <br> \
                    <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                    <p> Currently the Relative Value is <b>{1}</b>, which is above the upper threshold. It is advisable to pause your SIP and redeem some amount </p> \
                    <p> <u>Alert Details:</u> </p> \
                    <p> <b>Pause SIP:</b> Yes </p> \
                    <p> <b>Redeem:</b> {2} </p> \
                    <p> <b>Note:</b> {3} </p> <br> \
                    Thanks \
                    <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,redeem,note)
                else:
                    body_html = "Hi {0}, <br> \
                    <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                    <p> Currently the Relative Value is <b>{1}</b>, which is below the lower threshold. It is advisable to purchase some units now </p> \
                    <p> <u>Alert Details: </u> </p> \
                    <p> <b>Pause SIP:</b> No </p> \
                    <p> <b>Purchase:</b> {2} </p> \
                    <p> <b>Note:</b> {3} </p> <br> \
                    Thanks \
                    <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,purchase,note)
            else:
                if pause:
                    body_html = "Hi {0}, <br> \
                    <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                    <p> Currently the Relative Value is <b>{1}</b>, which is above the upper threshold. It is advisable to transfer some units to Nifty50 Index </p> \
                    <p> <u>Alert Details:</u> </p> \
                    <p> <b>Pause SIP:</b> Yes </p> \
                    <p> <b>Redeem and Transfer to Nifty50:</b> {2} </p> \
                    <p> <b>Note:</b> {3} </p> <br> \
                    Thanks \
                    <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,transfer_to_nifty50,note)
                else:
                    body_html = "Hi {0}, <br> \
                    <p> This is regarding an alert trigger with respect to your investment in <b>SmallCap Fund</b>. </p> \
                    <p> Currently the Relative Value is <b>{1}</b>, which is below the lower threshold. It is advisable to purchase some units now </p> \
                    <p> <u>Alert Details</u>: <p> \
                    <p> <b>Pause SIP:</b> No </p> \
                    <p> <b>Purchase:</b> {2} </p> \
                    <p> <b>Note:</b> {3} </p> <br> \
                    Thanks \
                    <hr>This is an Automated Email Notification from SIP Assistant Tool.".format(user_name,rounded_relative_value,purchase,note)
            

            msg_body = MIMEText(body_html, 'html')
            msg.attach(msg_body)

            mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            mail_server.login(mail_id,app_password)
            mail_server.sendmail(mail_id, recipients, msg.as_string())
            mail_server.close()

            insert_alert_data(email,True,relative_value)

    except Exception as err:
        logger.error(traceback.format_exc())

def insert_alert_data(email,status,relative_value):
    try:
        insert_data = {
            'date': datetime.today(),
            'email': email,
            'status': status,
            'relative_value': relative_value
        }
        alert_details.insert_one(insert_data)

        return True

    except Exception as err:
        logger.error(err,traceback.format_exc())


# ------------- LOAD CONFIG FILE ---------------------#

with open('./config.yml') as file:
    CONFIG = yaml.load(file, Loader=yaml.SafeLoader)

# ------------- FIXED VALUES -------------------------#

mode = CONFIG['mode']
upper_threshold = CONFIG['upper_threshold']
lower_threshold = CONFIG['lower_threshold']
tri_url = CONFIG['url']
headers = CONFIG['headers']
nifty_smallcap_initial = CONFIG['initial_tri']['Nifty Small Cap']
nifty_50_initial = CONFIG['initial_tri']['Nifty 50']
tri_initial = CONFIG['initial_tri']['tri_value']

data = {}

if mode == 'initialization':
    first_date = '02 Jan 2007'

    data['date']  = datetime.strptime(first_date, '%d %b %Y')
    data['nifty_smallcap_tri'] = float(nifty_smallcap_initial)
    data['nifty_50_tri'] = float(nifty_50_initial)
    data['relative_value'] = 1.00

# ------------- CONFIGURABLE -------------------------#

if mode == 'production':
    start_date = datetime.today()
else:
    start_date = datetime(2007,1,3)

end_date = datetime.today().date()

start_date = start_date.strftime("%d-%b-%Y")
end_date = end_date.strftime("%d-%b-%Y")

date_range = (start_date,end_date)
initial_values = (nifty_smallcap_initial, nifty_50_initial)

today_date = datetime.today().date()
today = datetime.combine(today_date, datetime.min.time())

# ------------- MAIN PROGRAM --------------------------#

if __name__ == '__main__':

    try:
        # ------------- LOGGER SETUP --------------------------#
        LOG_FILE_NAME = r"./services.log"
        handler = logging.handlers.RotatingFileHandler(filename=LOG_FILE_NAME,mode='a',maxBytes=1*1024*1024,backupCount=4)
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(thread)d - %(filename)s.%(funcName)s(%(lineno)d) - %(message)s',
        level = logging.INFO, handlers = [handler])
        logger=logging.getLogger(__name__)

        logger.info("\n")
        logger.info("*********************** STARTING SCRIPT ***********************")

        nifty_smallcap_data, nifty_50_data = fetch_data(tri_url,headers,date_range)
        logger.info(f"Successfully fetched the API data from {start_date} to {end_date}")

        total_api_data = (nifty_smallcap_data, nifty_50_data)
        
        total_dump_data = process_data(total_api_data,initial_values)
        logger.info(f"Successfully processed the data to seed to database")

        if data:
            total_dump_data.append(data)
        
        if total_dump_data:
            tri_collection.insert_many(total_dump_data)
            logger.info(f"Successfully inserted the data dump to the database")

            for data in total_dump_data:
                if data['date'] == today:
                    relative_value = data['relative_value']
                    if relative_value >= upper_threshold or relative_value <= lower_threshold:
                        scenario_1 = user_details.find({"subscription_option":1})
                        scenario_2 = user_details.find({"subscription_option":2})
                        scenario_3 = user_details.find({"subscription_option":3})
                        scenario_4 = user_details.find({"subscription_option":4})

                        threshold = (upper_threshold,lower_threshold)

                        total_user_details = (scenario_1,scenario_2,scenario_3,scenario_4)
                        alert_data = generate_alert_data(total_user_details,relative_value,threshold)
                        logger.info("Successfully fetched the alert data for the users")
                        send_alert_mail(alert_data,relative_value)
                        logger.info("Successfully sent the alert mails to the users, and updated alert table")
                    else:
                        logger.info(f"[{today}] No alert - Current relative value within threshold")
        else:
            logger.info(f"No new data found to insert into database")
        

    except Exception as err:
        logger.error(traceback.format_exc())


