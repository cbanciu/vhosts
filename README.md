#vhosts.py

This is a small python application to nicely display informations about Apache virtual hosts.


###Instalation

```sh
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py > vhosts.py
$ python vhosts.py
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

###Example

```sh
$ curl -s https://raw.githubusercontent.com/cbanciu/vhosts/master/vhosts.py | python -

SERVERNAME                    DOCUMENTROOT                            ACCESS_LOG                              ERROR_LOG                               CONFIG_FILE
dummy-host.example.com:80     /www/docs/dummy-host.example.com        logs/dummy-host.example.com-access_log  logs/dummy-host.example.com-error_log   /etc/httpd/conf/httpd.conf
host.example.com:80           /www/docs/host.example.com              logs/host.example.com-access_log        logs/host.example.com-error_log         /etc/httpd/conf.d/vhost.conf
www.host.example.com:80       /www/docs/host.example.com              logs/host.example.com-access_log        logs/host.example.com-error_log         /etc/httpd/conf.d/vhost.conf
```

### Requirements

* python 2.4 or newer

###Bugs/To Do

* It kinda works with Plesk
* It doesn't strip out quotes in names
* Check if Apache is running
