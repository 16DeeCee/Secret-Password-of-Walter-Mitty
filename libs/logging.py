import logging

logging.basicConfig(
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

class Logging:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)