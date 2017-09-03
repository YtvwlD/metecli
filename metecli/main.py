from . import log, cmdline

def run():
    log.setup(log.logging.DEBUG) # TODO
    cmdline.do(log=log)

if __name__ == '__main__':
    run()
