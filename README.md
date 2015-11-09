#vhosts.py

This is a small python application to nicely display informations about Apache virtual hosts.


###Instalation

```sh 
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py | python -
```
```sh
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py > vhosts.py
```

###Usage

```sh
$ python vhosts.py -h
Usage: vhosts.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d DOMAIN, --domain=DOMAIN
                        Display domain virtualhost info
```

### Requirments

* python 2.4 or newer

###Bugs

* It doesn't work with Plesk

