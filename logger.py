import logging
import logging.handlers

FORMAT = '%(name)s %(threadName)s (%(filename)s:%(lineno)s %(funcName)s): [%(levelname)s] %(message)s'
FORMAT_TS = "%(asctime)s {}".format(FORMAT)
DATEFMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format=FORMAT_TS, datefmt=DATEFMT)

# Formatter

def logger(name, filepath):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.addHandler(file(filepath))
    return log

def setdebug(log):
    log.setLevel(logging.DEBUG)

# Handlers
def syslog(facility = logging.handlers.SysLogHandler.LOG_LOCAL3):
    log = logging.handlers.SysLogHandler(
        facility = facility,
        address = '/dev/log'
    )
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
    log.setFormatter(formatter)
    return log

def file(filename):
    log = logging.handlers.WatchedFileHandler(
        filename = filename
    )
    formatter_ts = logging.Formatter(fmt=FORMAT_TS, datefmt=DATEFMT)
    log.setFormatter(formatter_ts)
    return log
