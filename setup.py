#! /usr/bin/env python3
# partly taken from https://github.com/pypa/sampleproject/blob/02130aeda025ca86975258f953b5d2531d74e94c/setup.py

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='metecli',

    # Versions should comply with PEP440.
    version='0.3.1',

    description='a cli for mete',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/YtvwlD/metecli',

    # Author details
    author='Niklas Sombert',
    author_email='niklas@ytvwld.de',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        
        # Where does it run?
        'Environment :: Console',
        
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        
        # Language
        'Natural Language :: English',
        
        # Topic
        'Topic :: Utilities',
        'Topic :: Internet',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='mete',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['metecli'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed.
    install_requires=['requests', 'PyYAML', 'tabulate'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'metecli=metecli.main:run',
        ],
    },
    
    # require (at least) Python 3.3
    python_requires="~=3.3",
)
