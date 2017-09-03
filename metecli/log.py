import logging

def setup(level=logging.WARNING):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=level)
    logging.debug("Initialized logging.")

debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical