import json
import requests
import time
import yaml

from eth_rpc_client import Client
client = Client(host="127.0.0.1", port="8545")


def padhexa(s):
    return s[2:].zfill(64)


def getDateTime(url, data, headers):

    try:
        result = requests.post(url + '/api/time', headers=headers, data=data)
        parsed_json = json.loads(result.text)
        return parsed_json['data']
    except json.JSONDecodeError as e:
        print(e)


def getEnergySum(url, data, headers, t0, t1):
    sumEnergy = 0

    result = requests.post(url + '/api/4/get/watts/by_time/' + str(t0) + '/' + str(t1), headers=headers, data=data)
    parsed_json = json.loads(result.text)
    print('=> 1 = ' + str(parsed_json['data']))

    for n in range(0, len(parsed_json['data'])):
        watt = int(parsed_json['data'][n]['value'])
        print('=> 2 = ' + str(parsed_json['data'][n]['value']))
        sumEnergy += watt

    return sumEnergy


with open("parameters.yml", 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# Defintion of pine used
pine = param["usedPine"]["id"]
pineURL = param[pine]["url"]
pineLogin = param[pine]["login"]
pinePswd = param[pine]["password"]
headers = {'Content-Type': 'application/json', }
data = 'login=' + pineLogin + '&password=' + pinePswd


time0 = getDateTime(pineURL, data, headers)
print(time0)

while 1:
    # delay to define
    time.sleep(20)
    time1 = getDateTime(pineURL, data, headers)
    sumWatt = getEnergySum(pineURL, data, headers, time0, time1)

    time0 = time1

    # Consumer
    if param[pine]['typ'] == 'C':
        # to update Energy balance (consumer)
        hashData = param['contract']['fctConsumeEnergy'] + padhexa(hex(sumWatt))
        # pine2 for debug (laptop)
        response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)

    # Producer
    else:
        # to update Energy balance (producer)
        # pine2 for debug (laptop)
        hashData = param['contract']['fctSetProduction'] + padhexa(hex(sumWatt))
        response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)
