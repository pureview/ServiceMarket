import datetime
import logging

logger=None

def get_logger():
    global logger
    if logger!=None: return logger
    now=datetime.datetime.now().strftime("%Y%m%d")
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler("/home/ubuntu/taobao/log/hand_log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger

if __name__=='__main__':
    logger=get_logger()
    logger.info('Test info')
