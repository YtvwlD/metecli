from . import log, cmdline, setup, account

log.setup(log.logging.DEBUG) # TODO

cmdline.do(log=log, setup_func=setup.do, account_func=account.do)
