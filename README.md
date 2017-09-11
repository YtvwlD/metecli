# metecli

[![Code Health](https://landscape.io/github/YtvwlD/metecli/master/landscape.svg?style=plastic)](https://landscape.io/github/YtvwlD/metecli/master)

This is a CLI for [mete](https://github.com/chaosdorf/mete/)
(or any other server supporting the [Space-Market API](https://github.com/Space-Market/API) [v1](https://space-market.github.io/API/preview/v1)).

## Getting Started

### Installation

Although this isn't strictly needed
you might want to install metecli first before using it.

Upgrading (or downgrading) is done the same way as installing.

#### Installing the current stable version

`sudo -H pip3 install metecli`

#### Installing the development version

1. Clone this repository. (`git clone https://github.com/YtvwlD/metecli.git`)
2. Install it. (`sudo -H ./setup.py install`)

#### Or just use it without installing

1. Clone this repository. (`git clone https://github.com/YtvwlD/metecli.git`)
2. Install the dependencies (either via your distribution's package manager or via pip):
   2.1. requests
   2.2. PyYAML
   2.3. tabulate
3. Start it. (`./run.sh`)
4. Remember to mentally replace `metecli` with `./run.sh` in the next sections.

### Configuration

The initial configuration is done by calling `metecli setup`. You'll see an exemplary invocation below:

```
$ metecli setup
Please enter the url for mete: http://mete/
The URL you entered doesn't use HTTPS. Do you want to try again? (y/n) n
WARNING:metecli.setup:Using HTTP. The connection won't be secure.
Please enter your username (or a part of it) or your uid: 1
```

metecli is now configured and ready.

## a few use-cases

### buy a drink

```
$ metecli account buy Mate
```

### deposit money

```
$ metecli account deposit 2.50
```

### show information about your account

```
$ metecli account show
+----------------------------------+---------+
| ID                               | 2       |
+----------------------------------+---------+
| name                             | test    |
+----------------------------------+---------+
| email                            |         |
+----------------------------------+---------+
| account balance                  | -1.50 € |
+----------------------------------+---------+
| active?                          | no      |
+----------------------------------+---------+
| log transactions?                | no      |
+----------------------------------+---------+
| redirect after buying something? | yes     |
+----------------------------------+---------+
```

### modify your account

```
$ metecli account modify
name [test]: 
email []: test@example.com
account balance [-1.5]: 
active? [no]: yes
log transactions? [no]:  
redirect after buying something? [yes]:
```

### list your recent transactions

You'll need to have the setting "log transactions" (`audit`) enabled for this to work.

```
$ metecli account logs
Audits for user 1:
+--------------------------+---------+--------------+
| time                     | drink   |   difference |
+==========================+=========+==============+
| 2017-09-11T09:01:23.816Z | Mate    |         -1.5 |
+--------------------------+---------+--------------+
| 2017-09-10T13:41:50.372Z | n/a     |         -5   |
+--------------------------+---------+--------------+
```

### list all drinks

```
$ metecli drinks list
All drinks:
+------+---------+---------------+------------+---------+-----------+
|   ID | name    |   bottle size | caffeine   | price   | active?   |
+======+=========+===============+============+=========+===========+
|    1 | Mate    |           0.5 |            | 1.50 €  | yes       |
+------+---------+---------------+------------+---------+-----------+
|    2 | Cola    |           0   |            | 1.50 €  | yes       |
+------+---------+---------------+------------+---------+-----------+
```

### display information about a drink

```
$ metecli drinks show Mate
+-------------+--------+
| ID          | 1      |
+-------------+--------+
| name        | Mate   |
+-------------+--------+
| price       | 1.50 € |
+-------------+--------+
| bottle size | 0.5    |
+-------------+--------+
| caffeine    |        |
+-------------+--------+
| active?     | yes    |
+-------------+--------+
```

### modify a drink

```
$ metecli drinks modify Mate
name [Mate]: 
price [1.5]: 
bottle size [0.5]: 
caffeine [None]: 100
active? [yes]:
```
