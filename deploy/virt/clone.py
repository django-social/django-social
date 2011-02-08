#!/usr/bin/env python

import libvirt
import os
import shlex
import subprocess
import sys

def usage():
    print '''
usage: %s <num>
    ''' % sys.argv[0]

# http://code.activestate.com/recipes/577058-query-yesno/download/1/
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


try:
    num = int(sys.argv[1])
    assert num > 0
except:
    usage()
    exit()

i = '%03d' % num
s2 = i[-2:]
s3 = i[-3:]

domain = 's%(s3)s' % locals()
image = '/var/lib/libvirt/images/%(s3)s.img' % locals()
mac = '52:54:00:90:00:%(s2)s' % locals()

conn = libvirt.open('qemu:///system')
assert conn

domains = conn.listDefinedDomains()
active_domains = []

for domain_id in conn.listDomainsID():
    _domain = conn.lookupByID(domain_id).name()
    domains.append(_domain)
    active_domains.append(_domain)

if domain in active_domains:
    if query_yes_no('Domain "%s" running. Destroy it?' % domain) == 'yes':
        subprocess.call(shlex.split('virsh destroy %s' % domain))
    else:
        exit()

if domain in domains:
    if query_yes_no('Domain "%s" already exists. Delete it?' % domain) == 'yes':
        subprocess.call(shlex.split('virsh undefine %s' % domain))
    else:
        exit()

if os.path.exists(image):
    if query_yes_no('Disk image "%s" already exists. Delete it?' % image) == 'yes':
        subprocess.call(shlex.split('virsh vol-delete %s' % image))
    else:
        exit()

subprocess.call(shlex.split('virt-clone --connect qemu:///system -o s000 -n %(domain)s -f %(image)s -m %(mac)s' % locals()))

if query_yes_no('Domain "%s" created. Start it?' % domain, default='yes') == 'yes':
    subprocess.call(shlex.split('virsh start %s' % domain))

