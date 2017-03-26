# #/usr/bin/env python3
# -*- coding:utf-8 -*-

import yaml

with open('config.yml', 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)


def getconfig():

    config = []

    # Smartcontract address
    contract = {'name': 'Contract', 'address': param['contract']['address']}
    config.append(contract.copy())

    nodes = param['nodes']['list']
    # Nodes info
    for node in nodes:
        nodeData = {'id': node, 'name': param['nodes'][node]['name'], 'address': param['nodes'][node]['address']}
        if param['nodes'][node]['type'] == 'P':
            nodeData['typ'] = 'producer'
        else:
            nodeData['typ'] = 'consumer'

        config.append(nodeData.copy())

    return config
