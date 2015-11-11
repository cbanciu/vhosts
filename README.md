#vhosts.py

This is a small python application to nicely display informations about Apache virtual hosts.


###Instalation

```sh
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py > vhosts.py
```

Or if you prefer running it directly from github

```sh 
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py | python -
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

### Requirements

* python 2.4 or newer

###Bugs/To Do

* It kinda works with Plesk
* It doesnt read next line in case of \ delimiter
* It doesn't strip out quotes in names
* Proper table alignment based on columns lenght
* Check if Apache is running
