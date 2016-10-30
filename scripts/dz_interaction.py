import json
import requests
import time
import yaml

from eth_rpc_client import Client
client = Client(host="127.0.0.1", port="8545")


def padhexa(s):
    return s[2:].zfill(64)


def padaddress(a):
    a = '000000000000000000000000' + a.strip('0x')
    return a


def getDateTime(url, data, headers):

    try:
        result = requests.post(url + '/api/time', headers=headers, data=data)
        parsed_json = json.loads(result.text)
        return parsed_json['data']
    except json.JSONDecodeError as e:
        print(e)


def getEnergySum(url, data, headers, t0, t1):
    sumEnergy = 0
    timestp = 0

    try:
        result = requests.post(url + '/api/4/get/watts/by_time/' + str(t0) + '/' + str(t1), headers=headers, data=data)
    except json.JSONDecodeError as e:
        print(e)
    else :
        parsed_json = json.loads(result.text)
        for n in range(0, len(parsed_json['data'])):
            # TODO : check data from citizenwatt
            if timestp < parsed_json['data'][n]['timestamp']:
                watt = int(parsed_json['data'][n]['value']/100) # /100 for test and debug
                sumEnergy += watt
                timestp = parsed_json['data'][n]['timestamp']
    return sumEnergy


with open("parameters.yml", 'r') as stream:
    try:
        param = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)


# Defintion of pine used to update data
pine = param['usedPine']['id']
pineURL = param[pine]['url']
pineLogin = param[pine]['login']
pinePswd = param[pine]['password']
headers = {'Content-Type': 'application/json', }
data = 'login=' + pineLogin + '&password=' + pinePswd


time0 = getDateTime(pineURL, data, headers)


while 1:
    # delay to define
    time.sleep(20)
    time1 = getDateTime(pineURL, data, headers)
    sumWatt = getEnergySum(pineURL, data, headers, time0, time1)

    print('time : ' + time.strftime("%D %H:%M:%S", time.localtime(int(time1))) + ', sumWatt = ' + str(sumWatt))

    time0 = time1

    if sumWatt !=0 :

        # Consumer
        if param[pine]['typ'] == 'C':

            # to update Energy balance (consumer)
            hashData = param['contract']['fctConsumeEnergy'] + padhexa(hex(sumWatt))
            # using pine2 directly for test and debug
            response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)

            # get the energy balance
            EnergyBalance = int(client.call(_from=param['pine2']['address'], to=param['contract']['address'], data=param['contract']['fctEnergyBalance'], block="latest"), 0)
            print('EnergyBalance = ' + str(EnergyBalance))

            # if energy balance is too low, a energy transaction is triggered
            if EnergyBalance < param['pine2']['limit']:
                watt = 1000
                seller = param['pine1']['address'].replace('0x', '')
                hashData = param['contract']['fctBuyEnergy'] + padaddress(seller) + padhexa(hex(watt))
                response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)


        # Producer
        else:
            # to update Energy balance (producer)
            hashData = param['contract']['fctSetProduction'] + padhexa(hex(sumWatt))
            response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)
