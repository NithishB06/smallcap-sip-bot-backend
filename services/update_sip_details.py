import pymongo
import traceback
import logging
import logging.handlers
from datetime import datetime
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    try:
        # ------------- INITIALIZATION --------------------#

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['smallcap_sip_bot']

        user_preferences = db['smallcap_bot_userpreferences']
        user_details = db['smallcap_bot_userdetails']

        # ------------- LOGGER SETUP --------------------------#

        LOG_FILE_NAME = r"./services.log"
        handler = logging.handlers.RotatingFileHandler(filename=LOG_FILE_NAME,mode='a',maxBytes=1*1024*1024,backupCount=4)
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(thread)d - %(filename)s.%(funcName)s(%(lineno)d) - %(message)s',
        level = logging.INFO, handlers = [handler])
        logger=logging.getLogger(__name__)

        logger.info("\n")
        logger.info("*********************** STARTING SCRIPT ***********************")

        # ------------- MAIN PROGRAM --------------------------#

        today_date = datetime.today().date()
        today = datetime.combine(today_date, datetime.min.time())

        to_update_preferences = list(user_preferences.find({"next_step_up_date": today}))

        if to_update_preferences:
            for record in to_update_preferences:
                email = record['email']
                current_sip_amount = record['current_sip_amount']
                step_up_percentage = record['step_up_percentage']

                new_sip_amount = current_sip_amount + (current_sip_amount * step_up_percentage / 100)
                new_step_up_date = today + relativedelta(years=1)
                
                to_update_details = list(user_details.find({"email": email}))

                ### --- UPDATE IN USER PREFERENCE COLLECTION --- ###
                user_preferences.update_one({
                    'email': email
                },{
                    '$set': {
                        'current_sip_amount': new_sip_amount,
                        'next_step_up_date': new_step_up_date
                    }
                })

                ### --- UPDATE IN USER DETAILS COLLECTION --- ###
                user_details.update_one({
                    'email': email
                },{
                    '$set': {
                        'sip_amount': new_sip_amount
                    }
                })

                logger.info(f"Successfully updated SIP Amount and Next Step Up Date for email - {email}")

        else:
            logger.info(f"No records found to be updated for {today_date}")

    except Exception as err:
        logger.error(traceback.format_exc())



