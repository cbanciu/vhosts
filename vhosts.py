#!/usr/bin/env python
"""Application to nicely display informations about Apache Virtual Hosts"""

import platform
from glob import glob
import itertools
import os
import re
from sys import exit
from optparse import OptionParser


class bcolors:
    """
        This class is to display different colour fonts
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    UNDERLINE = '\033[4m'

def get_distro():
    """Name of your Linux distro"""
    return platform.dist()[0].lower()


def apache_files():
    if get_distro() in ("centos", "redhat"):
        webserver = "httpd"
        apache_conf = "/etc/httpd/conf/httpd.conf"
        apache_root = "/etc/httpd/"
    elif get_distro() in ("ubuntu", "debian"):
        webserver = "apache2"
        apache_conf = "/etc/apache2/apache2.conf"
        apache_root = "/etc/apache2/"
    else:
        print bcolors.FAIL + "This application only works on RedHat, Ubuntu or Debian" + bcolors.ENDC
        exit(1)
    return webserver, apache_conf, apache_root

def get_conf_files(f):
    """Get a list of Apache config files starting from httpd.conf or apache2.conf"""
    apache_conf = apache_files()[1]
    apache_root = apache_files()[2]
    conf_files = [[apache_conf]]
    try:
        fi = open(f, "r")
    except:
        print bcolors.FAIL + "Cannot open Apache config file. Is Apache installed?" + bcolors.ENDC
        exit(1)
    for line in iter(fi):
        if line.strip().lower().startswith("include") or line.strip().lower().startswith("includeoptional"):
            line_to_add = line.strip().split(" ")[1]
            if line_to_add[0] in ('"', "'") and line_to_add[0] == line_to_add[-1]:
                line_to_add = line_to_add[1:-1]
            if not line_to_add.strip().startswith("/"):
                line_to_add = apache_root+line_to_add
            if os.path.isdir(line_to_add):
                file_to_add = glob(line_to_add+'/*')
                conf_files.append(file_to_add)
            else:
                file_to_add = glob(line_to_add)
                conf_files.append(file_to_add)
            for files in file_to_add:
               get_conf_files(files)
    fi.close()
    return list(set(itertools.chain(*conf_files)))

def get_line(ln,st):
    if ln.lower().strip().startswith(st):
        if st.lower().strip() == "<virtualhost":
            return ln.strip().partition(':')[-1].rpartition('>')[0] or "80"
        if st.lower().strip() == "serveralias":
            return re.sub(r'^(\w+ )',r'', ln.strip())
        else:
            return ln.strip().split()[1] 
    else:
        return "-"

def get_vhosts():
    """Iterate through vhost list and get everything between <VirtualHost> and </VirtualHost>"""
    apache_conf = apache_files()[1]
    vhosts_files = get_conf_files(apache_conf)
    all_vhosts = []
    vhost = None
    in_vhost = False
    for v in vhosts_files:
        fi = open(v, "r")
        for line in fi:
            if not in_vhost and line.lower().startswith('<virtualhost'):
                in_vhost = True
                vhost = []
            elif in_vhost and line.lower().startswith('</virtualhost>'):
                in_vhost = False
                all_vhosts.append("ConfigFile " + v + "\n" + ''.join(vhost) + '</Virtualhost>')
                vhost = None
            if in_vhost:
                vhost.append(line)
    return all_vhosts

def test_string(vhost_list,text):
    s = vhost_list.splitlines()
    for i in s:
        if get_line(i,text) is "-":
            get_line(i,text)
        else: 
            return  get_line(i,text)
    return get_line(i,text)

def get_vhost_dict():
    """Parse vhost list and generates the following dictionary:
    {"SERVERNAME|SERVERALIAS": [DOCUMENTROOT], [ACCESS_LOG], [ERROR_LOG], [CONFIG_FILE]}"""

    sites = get_vhosts()
    vhost_dict = {}
    for site in sites:
        if test_string(site,"servername") is not "-": #!= "-":
            vhost_dict[test_string(site,"servername")+":"+test_string(site,"<virtualhost")] = [test_string(site,"documentroot")] + \
            [test_string(site,"customlog")] + \
            [test_string(site,"errorlog")] + \
            [test_string(site,"configfile")]
        if test_string(site,"serveralias") is not "-":
            for s_alias in test_string(site,"serveralias").split():
                vhost_dict[s_alias+":"+test_string(site,"<virtualhost")] = [test_string(site,"documentroot")] + \
                [test_string(site,"customlog")] + \
                [test_string(site,"errorlog")] + \
                [test_string(site,"configfile")]
    return vhost_dict


def print_header():
    text_header = "DOCUMENTROOT ACCESS_LOG ERROR_LOG CONFIG_FILE"
    try:
        print bcolors.HEADER + "{:30}".format("SERVERNAME") + "" .join("{:35}".format(k) for k in text_header.split()) + bcolors.ENDC
    except:
        print bcolors.HEADER + "SERVERNAME".ljust(30) + "".join(k.ljust(35) for k in text_header.split()) + bcolors.ENDC

def list_vhost(vhost):
    vhost_dict = get_vhost_dict()
    keys = [key for key in vhost_dict.keys() if key.startswith(vhost)]
    if keys:
        print_header()
        for key in keys:
            try: #print i," ".join(vhost_dict[i])
                print bcolors.OKBLUE + '{:30}'.format(key) + bcolors.ENDC + "".join("{:35}".format(v) for v in vhost_dict[key])
            except:
                print bcolors.OKBLUE + key.ljust(30) + bcolors.ENDC + "".join(value.ljust(35) for value in vhost_dict[key])
    else:
        print "ServerName or ServerAlias " + bcolors.BOLD + vhost + bcolors.ENDC + \
        " doesn't seem to be defined in your Apache configuration"


def list_all():
    vhost_dict = get_vhost_dict()
    print_header()
    for value,key  in sorted([(value,key) for (key,value) in vhost_dict.items()]):
        try:
            print bcolors.OKBLUE + '{:30}'.format(key) + " " + bcolors.ENDC + "".join('{:35}'.format(v) for v in value)
        except:
            print bcolors.OKBLUE + key.ljust(30) + bcolors.ENDC + "".join(v.ljust(35) for v in value)

def main():
    #parser = ArgumentParser(description="Nicely display Apache virtual hosts info")
    #parser.add_argument("-d", "--domain", help="Display domain(s) virtualhost info", nargs="*", type=str)
    #args = parser.parse_args()
    #if args.domain:
    #    print_header()
    #    for domain in args.domain:
    #        list_vhost(domain)
    #else:
    #    list_all()
    
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 0.6-beta", add_help_option=True) 
    parser.add_option("-d", "--domain", help="Display domain virtualhost info", dest="domain", action="store")
    (options, args) = parser.parse_args()

    if options.domain:
        for dom in options.domain.split():
            list_vhost(dom)
    else:
        list_all()

if __name__ == "__main__":
    main()