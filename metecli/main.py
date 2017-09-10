def fail_on_python2():
    """Exits if we are using Python 2."""
    import sys
    if sys.version_info.major == 2:
        print("You are still using Python 2. Please upgrade.")
        sys.exit(-1)

def run():
    fail_on_python2()
    from . import cmdline
    cmdline.do()

if __name__ == '__main__':
    run()
