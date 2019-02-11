import logging
import logging.handlers

import traceback


class Log:
    """
    Custom logger
    """
    __logger = logging.getLogger("TapiocaPerlo")
    __logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)s|%(asctime)s] %(message)s")

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    __logger.addHandler(streamHandler)

    fileHandler = logging.FileHandler('TapiocaPerlo.log')
    fileHandler.setFormatter(formatter)
    __logger.addHandler(fileHandler)

    @classmethod
    def debug(cls, message):
        cls.__logger.debug(message)

    @classmethod
    def info(cls, message):
        cls.__logger.info(message)

    @classmethod
    def warning(cls, message):
        cls.__logger.warning(message)

    @classmethod
    def error(cls, message, trace_exc=True):
        if trace_exc:
            cls.__logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            cls.__logger.error(message)

    @classmethod
    def critical(cls, message):
        cls.__logger.critical(message)
