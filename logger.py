#logger.py
#logs all trades and errors

import logging
import os
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")

log_name = datetime.now().strftime("logs/%Y-%M-%M.log")

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
    handlers = [
        logging.FileHandler(log_name),
        logging.StreamHandler
    ]
)

def log(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def log_warn(message):
    logging.warning(message)