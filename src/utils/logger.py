import logging
from config.settings import SAppSettings


log_level = getattr(logging, SAppSettings.log_level.upper(), logging.INFO)

logger = logging.getLogger("Logger")
logger.setLevel(log_level)
logger.propagate = False

log_format = (
    "%(asctime)s\t%(name)s\t%(levelname)s\t"
    "%(filename)s:%(lineno)d\t%(message)s"
)
formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(SAppSettings.log_file, mode="a")
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)