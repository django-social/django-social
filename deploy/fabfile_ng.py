# -*- coding: utf-8 -*-

import re
import os
from hashlib import md5
from datetime import datetime
from getpass import getpass
from socket import gethostbyname, gethostbyaddr

from fabric.api import run, local, cd, env
from fabric.contrib.files import exists, contains, comment, uncomment, append, sed
from fabric.operations import put
from fabric.decorators import roles

env.roledefs.update({
    'all': ['s%03d.lan' % x for x in range(1, 21) ],
    'app': [ 'as%d.lan' %x for x in (1, 2, 3, 4,) ],
    'db': [ 'db%d.lan' %x for x in (1, 2, 3, 4,) ],
    'dbc': [ 'dbc%d.lan' %x for x in (1, 2,) ],
    'mysql': [ 'mysql%d.lan' %x for x in (1,) ],
    'memcached': [ 'memcached%d.lan' %x for x in (1,) ],
})




env.user = 'root'

env.warn_only = True

def uptime():
    run('uptime')

def eth0_addr():
    run('ifconfig eth0 | grep "inet addr"')

def initialize_server():
    upgrade_server()
    autoremove()
    install_git()
    install_etckeeper()
    install_server_software()

def upgrade_server():
    run('apt-get update')
    run('apt-get --yes dist-upgrade upgrade')

def install_git():
    run('apt-get --yes install git')
    run('git config --global user.name root')
    run('git config --global user.email root@mail.ru')

def install_etckeeper():
    run('apt-get --yes install etckeeper')
    comment('/etc/etckeeper/etckeeper.conf', '^VCS' )
    uncomment('/etc/etckeeper/etckeeper.conf', 'VCS="git"')
    run('etckeeper init')

def autoremove():
    run('apt-get --yes autoremove')

def install_server_software():
    put('packages.list', '/tmp/packages.list')
    try:
        run('apt-get install --yes `cat /tmp/packages.list`')
    finally:
        run('rm /tmp/packages.list')



# memcached
@roles('memcached')
def install_memcached():
    run('apt-get --yes install memcached')
    comment('/etc/memcached.conf', '^-l')
    append('/etc/memcached.conf', '-l 0.0.0.0')
    restart_memcached()

@roles('memcached')
def restart_memcached():
    run('service memcached restart')


# passwords

def _base62_encode(num):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphabet = "23456789abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ"
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

_salt = None
def gen_password(service, user):
    global _salt
    if not _salt:
        env_salt = os.getenv('FAB_PASSWORD_SALT')
        if env_salt:
            _salt = env_salt
        else:
            _salt = getpass('Enter salt for password generation:')
        _salt = _salt.strip()

    host = env.host

    if not host or not _salt:
        raise Exception('Empty data')

    ip = gethostbyname(host)
    host = gethostbyaddr(ip)[0]

    password = '-'.join([_salt, host, service, user])
    password = md5(password).hexdigest()
    return password

def print_password(service, user):
    print gen_password(service, user)

def gen_password_short(service, user):
    return _base62_encode(int(gen_password(service, user)[:12], 16))

def print_password_short(service, user):
    print gen_password_short(service, user)

# passwords end

# mysql
def install_mysql():
    password = gen_password('mysql', 'root')
    run('DEBIAN_FRONTEND=noninteractive apt-get --yes install mysql-server')
    run('mysqladmin -u root password %s' % password)
    #run('''echo "UPDATE user SET Password=PASSWORD('%s') WHERE User='root' ; FLUSH PRIVILEGES" | mysql -u root mysql''' % password)

def restart_mysql():
    run('service mysql-server restart')

def reset_mysql_password():
    password = gen_password('mysql', 'root')
    run('service mysql stop')
    run('mysqld --skip-grant-tables &')
    run('''echo "UPDATE user SET Password=PASSWORD('%s') WHERE User='root' ; FLUSH PRIVILEGES" | mysql -u root mysql''' % password)
    run('killall mysqld')
    run('service mysql start')
    
# mysql end

# zabbix
def install_zabbix_server():
    mysql_root_password = gen_password('mysql', 'root')
    mysql_zabbix_password = gen_password('mysql', 'zabbix')
    zabbix_password = gen_password_short('zabbix', 'Admin')

    try:
        #run('echo dbconfig-common dbconfig-common/mysql/admin-pass password %s | debconf-set-selections' % mysql_root_password)
        run('echo zabbix-server-mysql zabbix-server-mysql/mysql/admin-pass password %s | debconf-set-selections' % mysql_root_password)
        run('echo zabbix-frontend-php zabbix-frontend-php/mysql/admin-pass password %s | debconf-set-selections' % mysql_root_password)

        run('echo zabbix-server-mysql zabbix-server-mysql/mysql/app-pass password %s | debconf-set-selections' % mysql_zabbix_password)
        run('echo zabbix-frontend-php zabbix-frontend-php/mysql/app-pass password %s | debconf-set-selections' % mysql_zabbix_password)

        run('DEBIAN_FRONTEND=noninteractive apt-get --yes install zabbix-server-mysql')
        run('DEBIAN_FRONTEND=noninteractive apt-get --yes install zabbix-frontend-php')

        run('''echo "UPDATE users SET passwd=md5('%s') WHERE alias='Admin';" | mysql -uzabbix -p%s zabbix''' % (zabbix_password, mysql_zabbix_password))
    finally:
        for password_entry in (
                'zabbix-server-mysql zabbix-server-mysql/mysql/admin-pass',
                'zabbix-frontend-php zabbix-frontend-php/mysql/admin-pass',
                'zabbix-server-mysql zabbix-server-mysql/mysql/app-pass',
                'zabbix-frontend-php zabbix-frontend-php/mysql/app-pass',
                ):

            run('echo %s password | debconf-set-selections' % password_entry)

    php_ini = '/etc/php5/apache2/php.ini'
    sed(php_ini, ';[[:space:]]*date.timezone[[:space:]]*=', 'date.timezone = Europe/Moscow')
    sed(php_ini, '[[:space:]]*post_max_size[[:space:]]*=.*', 'post_max_size = 32M')
    sed(php_ini, '[[:space:]]*max_execution_time[[:space:]]*=.*', 'max_execution_time = 300')
    sed(php_ini, '[[:space:]]*max_input_time[[:space:]]*=.*', 'max_input_time = 300')
    run('service apache2 restart')

# zabbix end


