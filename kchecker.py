#!/usr/bin/python

DOCUMENTATION = """
---
module: kchecker.py
short_description: check if kerberos is configured as expected
options:
  username:
  - kerberos username
  password:
  - kerberos password
"""

from ansible.module_utils.basic import AnsibleModule

import os
import kerberos
import configparser

def remove():
    if os.path.exists('/tmp/tmp-krb5.ini'):
         os.remove('/tmp/tmp-krb5.ini')
         
def domain_maker():

    hostname = os.uname()[1]
    domain_list = hostname.split('.')
    pop_domain = domain_list.pop(0)
    domain = ".".join(domain_list)
    return domain

def service_maker():
    try:
        domain
    except NameError:
        domain = domain_maker()
        return f"host/{domain}"
    else:
        return f"host/{domain}"

def kerpy():
    cc = []
    remove()
    with open('/etc/krb5.conf', 'r') as f:
        line = f.readlines()
        for i,x in enumerate(line):
            space = len(x) - len(x.lstrip())
            if space >= 2:
                cc.append(x)
            elif x.startswith('['):
                cc.append(x)

    with open('/tmp/tmp-krb5.ini','a') as f:
        for line in cc:
            f.write(line.lower())

def pars(realm):
    kerpy()
    
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read('/tmp/tmp-krb5.ini')

    try:
        realms = parser['realms'][realm]
    except KeyError:
        results = False
    else:
        results = True
    return results

def admin(username, password, realm):
    service = service_maker()
    try:
        kerberos.checkPassword(username, password, service, realm)
    except kerberos.BasicAuthError:
        results = False
        return results
    else:
        results = True
        return results

def main():

    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        realm=dict(type='str', required=False),
    )

    module = AnsibleModule(
            argument_spec=module_args
            )

    if module.params['realm'] == None:
        module.params['realm'] = domain_maker().upper()

    username = module.params['username']
    password = module.params['password']
    realm = module.params['realm']
    test1 = pars(realm)

    if test1:
        test2 = admin(username,password,realm)
        results = True
    else:
        results = False

    result = {'results':{'test_results':results,'domain': domain_maker(), 'realm': realm}}
    module.exit_json(**result)


if __name__ == '__main__':
    main()
