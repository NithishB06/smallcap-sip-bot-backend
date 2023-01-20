import pymongo
import logging
import logging.handlers
import traceback

# ------------- MAIN PROGRAM --------------------------#

if __name__ == '__main__':
    try:
        # ------------- LOGGER SETUP --------------------------#
        LOG_FILE_NAME = r"../services.log"
        handler = logging.handlers.RotatingFileHandler(filename=LOG_FILE_NAME,mode='a',maxBytes=1*1024*1024,backupCount=4)
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(thread)d - %(filename)s.%(funcName)s(%(lineno)d) - %(message)s',
        level = logging.INFO, handlers = [handler])
        logger=logging.getLogger(__name__)

        logger.info("\n")
        logger.info("*********************** DELETING ALL DOCUMENTS OF [TotalReturnsIndex_Data] COLLECTION ***********************")

        # ------------- INITIALIZATION --------------------#

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['smallcap_sip_bot']

        tri_collection = db['smallcap_bot_totalreturnsindex_data']

        # ------------- CLEAR ALL RECORDS --------------------#

        tri_collection.delete_many({})

        logger.info("Deleted all documents of collection [TotalReturnsIndex_Data]")
    
    except Exception as err:
        logger.error(traceback.format_exc())

