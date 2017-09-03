from . import log, cmdline

log.setup(log.logging.DEBUG) # TODO

cmdline.do(log=log)
