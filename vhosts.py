#!/usr/bin/env python
"""Application to nicely display informations about Apache Virtual Hosts"""

import subprocess
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


def apache_files():
    """Get Apache HTTPD_ROOT and SERVER_CONFIG_FILE"""

    if subprocess.call("type " + "apache2ctl", shell=True, stdout=subprocess.PIPE, stderr=open('/dev/null', 'w')) == 0:
        command = 'apache2ctl -V 2>/dev/null | egrep "SERVER_CONFIG_FILE|HTTPD_ROOT" | cut -d= -f2'
    elif subprocess.call("type " + "apachectl", shell=True, stdout=subprocess.PIPE, stderr=open('/dev/null', 'w')) == 0:
        command = 'apachectl -V 2>/dev/null | egrep "SERVER_CONFIG_FILE|HTTPD_ROOT" | cut -d= -f2'
    else:
        print bcolors.FAIL + "Cannot open Apache config file. Is Apache installed?" + bcolors.ENDC
        exit(1)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    apache_files = proc.stdout.read().split()
    for i in range(2):
        if apache_files[i][0] in ('"', "'") and apache_files[i][0] == apache_files[i][-1]:
            apache_files[i] = apache_files[i][1:-1]
    if apache_files[1][0] is not "/":
        apache_files[1] = apache_files[0]+"/"+apache_files[1]
    return apache_files


def get_conf_list(f_list):
    """Get a list of Apache config files starting from httpd.conf or apache2.conf"""

    apache_root = apache_files()[0]+"/"
    conf_files = []
    lines = []
    for f in f_list:
        try:
            fi = open(f, "r")
        except:
            print "Cannot open config file."
            pass
        for line in iter(fi):
            if line.strip().lower().startswith("include") or line.strip().lower().startswith("includeoptional"):
                lines_to_add = line.strip().split()[1]
                lines.append(lines_to_add)
        for line_to_add in lines:
            if line_to_add[0] in ('"', "'") and line_to_add[0] == line_to_add[-1]:
                line_to_add = line_to_add[1:-1]

            if not line_to_add.strip().startswith("/"):
                line_to_add = apache_root+line_to_add

            if os.path.isdir(line_to_add):
               conf_files.append(glob(line_to_add+'/*'))

            if not os.path.isdir(line_to_add):
                conf_files.append(glob(line_to_add))

    return list(set(itertools.chain(*conf_files)))


def get_conf_files():
    """Get a list of Apache config files starting from httpd.conf or apache2.conf"""

    n = 0
    apache_conf = [apache_files()[1]]
    new_list = [apache_conf + get_conf_list(apache_conf)]
    while True:   #n = n + 1
        new_list.append(get_conf_list(new_list[n]))
        if len(new_list[-1]) > 0:
            new_list.append(get_conf_list(new_list[n]))
            n = n + 1
        else:
            break
    return list(set(itertools.chain(*new_list)))


def get_line(ln, st):
    if ln.lower().strip().startswith(st):
        if st.lower().strip() == "<virtualhost":
            try:
                return re.search(r'\:(.*)\>', ln.strip(":")).group(1)
            except:
                return "80"
        if st.lower().strip() == "serveralias":
            return re.sub(r'^(\w+ )', r'', ln.strip())
        else:
            return ln.strip().split()[1]
    else:
        return "-"


def get_vhosts():
    """Iterate through vhost list and get everything between <VirtualHost> and </VirtualHost>"""
    apache_conf = apache_files()[1]
    vhosts_files = get_conf_files()
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


def test_string(vhost_list, text):
    s = vhost_list.splitlines()
    for i in s:
        res = get_line(i,text)
        if res != "-":
            return res
    return "-"


def get_vhost_dict():
    """Parse vhost list and generates the following dictionary:
    {"SERVERNAME|SERVERALIAS": [DOCUMENTROOT], [ACCESS_LOG], [ERROR_LOG], [CONFIG_FILE]}"""

    sites = get_vhosts()
    vhost_dict = {}
    for site in sites:
        if test_string(site, "servername") is not "-":
            vhost_dict[test_string(site, "servername") + ":" + test_string(site, "<virtualhost")] = [test_string(site, "documentroot")] + \
            [test_string(site, "customlog")] + \
            [test_string(site, "errorlog")] + \
            [test_string(site, "configfile")]
        if test_string(site, "serveralias") is not "-":
            for s_alias in test_string(site, "serveralias").split():
                vhost_dict[s_alias + ":" + test_string(site, "<virtualhost")] = [test_string(site, "documentroot")] + \
                [test_string(site,"customlog")] + \
                [test_string(site,"errorlog")] + \
                [test_string(site, "configfile")]
    return vhost_dict

def get_longest_element():
    vhost_dict = get_vhost_dict()
    longest_element = max(len(v) for v in vhost_dict.values())
    return longest_element


def print_header():
    print get_longest_element()
    text_header = "DOCUMENTROOT ACCESS_LOG ERROR_LOG CONFIG_FILE"
    try:
        print bcolors.HEADER + "{:30}".format("SERVERNAME") + "" .join("{:45}".format(k) for k in text_header.split()) + bcolors.ENDC

    except:
        print bcolors.HEADER + "SERVERNAME".ljust(30) + "".join(k.ljust(45) for k in text_header.split()) + bcolors.ENDC


def list_vhost(vhost):
    vhost_dict = get_vhost_dict()
    keys = [key for key in vhost_dict.keys() if key.startswith(vhost)]
    if keys:
        print_header()
        for key in keys:
            try:
                print bcolors.OKBLUE + '{:30}'.format(key) + bcolors.ENDC + "".join("{:45}".format(v) for v in vhost_dict[key])
            except:
                print bcolors.OKBLUE + key.ljust(30) + bcolors.ENDC + "".join(value.ljust(45) for value in vhost_dict[key])
    else:
        print "ServerName or ServerAlias " + bcolors.FAIL + vhost + bcolors.ENDC + \
            " doesn't seem to be defined in your Apache configuration"



def list_all():
    vhost_dict = get_vhost_dict()
    print_header()
    for value, key in sorted([(value, key) for (key, value) in vhost_dict.items()]):
        try:
            print bcolors.OKBLUE + '{:30}'.format(key) + " " + bcolors.ENDC + "".join('{:45}'.format(v) for v in value)
        except:
            print bcolors.OKBLUE + key.ljust(30) + bcolors.ENDC + "".join(v.ljust(45) for v in value)


def main():
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

