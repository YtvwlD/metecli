#!/bin/sh

# see https://stackoverflow.com/a/7166368/2192464

python3 -c "import metecli.main; import cProfile; cProfile.run('metecli.main.run()', 'metecli.profile')" $@
