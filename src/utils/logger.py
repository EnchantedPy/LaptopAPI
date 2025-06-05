from config.settings import BASE_DIR
from yaml import safe_load
from logging.config import dictConfig
import logging

config_file_path = BASE_DIR / 'logging.yaml'


with open(config_file_path, 'r', encoding='utf-8') as f:
	log_config_dict = safe_load(f)
   
    
dictConfig(log_config_dict)

logger = logging.getLogger("logger")
test_logger = logging.getLogger("test_logger")