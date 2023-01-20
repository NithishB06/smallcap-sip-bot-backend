import pymongo
import logging
import logging.handlers
import traceback

# ------------- MAIN PROGRAM --------------------------#

if __name__ == '__main__':
    try:
        # ------------- LOGGER SETUP --------------------------#
        LOG_FILE_NAME = r"../user_data.log"
        handler = logging.handlers.RotatingFileHandler(filename=LOG_FILE_NAME,mode='a',maxBytes=1*1024*1024,backupCount=4)
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(thread)d - %(filename)s.%(funcName)s(%(lineno)d) - %(message)s',
        level = logging.INFO, handlers = [handler])
        logger=logging.getLogger(__name__)

        logger.info("\n")
        logger.info("*********************** VIEW ALL DOCUMENTS OF [UserPreferences, UserDetails, Alerts ] COLLECTIONS ***********************")

        # ------------- INITIALIZATION --------------------#

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['smallcap_sip_bot']

        user_preferences = db['smallcap_bot_userpreferences']
        user_details = db['smallcap_bot_userdetails']
        alert_details = db['smallcap_bot_alerts']


        # ------------- CLEAR ALL RECORDS --------------------#

        user_preferences_documents = list(user_preferences.find({}))
        user_details_documents = list(user_details.find({}))
        alert_details_documents = list(alert_details.find({}))

        if user_preferences_documents:
            logger.info("[USER PREFERENCES, USER DETAILS] :- ")
            logger.info("===================================")
            for document in user_preferences_documents:
                id = document['_id']
                email = document['email']
                user_name = document['user_name']
                current_sip_amount = document['current_sip_amount']
                step_up_percentage = document['step_up_percentage']
                step_up_month = document['step_up_month']
                subscription_option = document['subscription_option']
                last_updated_date = document['last_updated_date']
                next_step_up_date = document['next_step_up_date']

                logger.info(f"_id -> {id}")
                logger.info(f"email -> {email}")
                logger.info(f"user_name -> {user_name}")
                logger.info(f"current_sip_amount -> {current_sip_amount}")
                logger.info(f"step_up_percentage -> {step_up_percentage}")
                logger.info(f"step_up_month -> {step_up_month}")
                logger.info(f"subscription_option -> {subscription_option}")
                logger.info(f"last_updated_date -> {last_updated_date}")
                logger.info(f"next_step_up_date -> {next_step_up_date}")

                for record in user_details_documents:
                    if record['email'] == email:
                        id_2 = record['_id']
                        email_2 = record['email']
                        user_name_2 = record['user_name']
                        subscription_option_2 = record['subscription_option']
                        sip_amount_2 = record['sip_amount']

                        logger.info("-----------------------------------")
                        logger.info(f"_id -> {id_2}")
                        logger.info(f"email -> {email_2}")
                        logger.info(f"user_name -> {user_name_2}")
                        logger.info(f"subscription_option -> {subscription_option_2}")
                        logger.info(f"sip_amount -> {sip_amount_2}")
                
                logger.info("===================================")
        else:
            logger.info("No User Preferences and User Details Documents found in the Collection")
        
        if alert_details_documents:
            logger.info("[ALERT DETAILS] :- ")
            logger.info("==================")
            for document in alert_details_documents:
                id = document['_id']
                date = document['date']
                email = document['email']
                status = document['status']
                relative_value = document['relative_value']

                logger.info("------------------")
                logger.info(f"_id -> {id}")
                logger.info(f"date {date}")
                logger.info(f"email -> {email}")
                logger.info(f"status -> {status}")
                logger.info(f"relative_value -> {relative_value}")

        else:
            logger.info("No Alert Details Documents found in the collection")
    
    except Exception as err:
        logger.info(traceback.format_exc())
