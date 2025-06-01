import logging
from pathlib import Path
from config.settings import Settings, TestSettings

LOG_FORMAT = (
    "%(asctime)s\t%(name)s\t%(levelname)s\t"
    "%(filename)s:%(lineno)d\t%(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

def setup_logger(name: str, log_file: str, level=logging.INFO, stream: bool = True):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


logger = setup_logger(
    name="Logger",
    log_file=Path("logs/app.log"),
    level=getattr(logging, Settings.log_level.upper(), logging.INFO)
)

test_logger = setup_logger(
    name="tests",
    log_file=Path("logs/tests.log"),
    level=getattr(logging, TestSettings.log_level.upper(), logging.DEBUG)
)
