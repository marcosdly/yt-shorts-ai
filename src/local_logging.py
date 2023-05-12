import logging, os
from logging.handlers import WatchedFileHandler
from config.config_wrapper import LOGS_FOLDER


class MasterLogger:
    def __generateLogger(level: int) -> logging.Logger:
        formatter = logging.Formatter(
            # !! at the beginning of every line to make new lines a little easier to spot
            fmt="!!%(asctime)s::%(levelname)s:%(threadName)s: %(message)s",
            datefmt="%A, %d/%m/%Y %H:%M:%S") # Saturday, 23/05/2023 20:54:59
        handler = WatchedFileHandler(filename=os.path.join(LOGS_FOLDER, "general.log"),
                                    encoding="utf-8")
        handler.setFormatter(formatter)

        level_name = ""
        match level:
            case logging.INFO:
                level_name = "INFO"
            case logging.DEBUG:
                level_name = "DEBUG"
            case logging.ERROR:
                level_name = "ERROR"
            case logging.WARNING:
                level_name = "WARNING"
            case logging.CRITICAL:
                level_name = "CRITICAL"
            case _:
                raise TypeError("Incorrect log level integer representation.")

        log = logging.getLogger(f"{level_name}_Logger")
        log.addHandler(handler)
        log.setLevel(level)
        return log
    
    __info_logger = __generateLogger(logging.INFO)
    __warning_logger = __generateLogger(logging.WARNING)
    __debug_logger = __generateLogger(logging.DEBUG)
    __error_logger = __generateLogger(logging.ERROR)
    __critical_logger = __generateLogger(logging.CRITICAL)
    
    @classmethod
    def info(cls, msg, *args, **kwargs):
        cls.__info_logger.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        cls.__warning_logger.warning(msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        cls.__debug_logger.debug(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        cls.__error_logger.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        cls.__critical_logger.critical(msg, *args, **kwargs)

    def __init__(self) -> None:
        raise SyntaxError("This class can't be instantiated.")


# alias; can be done with from [module] import Class as log
log = MasterLogger