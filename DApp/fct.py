# #/usr/bin/env python3
# -*- coding:utf-8 -*-

import yaml

with open('config.yml', 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)


def getconfig():

    # Node info
    config = {'name': param['nodes']['node0']['name'], 'address': param['nodes']['node0']['address']}
    if param['nodes']['node0']['type'] == 'P':
        config['typ'] = 'producer'
    else:
        config['typ'] = 'consumer'

    # Smartcontract address
    config['contract'] = param['contract']['address']

    return config
