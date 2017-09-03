from . import cmdline

import logging

def run():
    logging.basicConfig(level=logging.DEBUG) # TODO
    cmdline.do()

if __name__ == '__main__':
    run()
