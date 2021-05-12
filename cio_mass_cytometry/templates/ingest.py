import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger()
import pandas as pd

def read_excel_template(template_path,mylogger):
    logger = mylogger
    # Read in each part of the spreadsheet
    logger.info("Read the parameters")