import json
import requests
import serial
import time
import yaml

from eth_rpc_client import Client
client = Client(host="127.0.0.1", port="8545")

ser = serial.Serial('/dev/ttyACM2', 9600) #to update
relai4_status = 0
lampStatus = 0


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


def turnRelay(relai):
    global relai4_status

    if(relai == "4"):
        if relai4_status == 0:
            ser.write(str("4").encode())
            relai4_status = 1
        else:
            ser.write(str("4").encode())
            relai4_status = 0

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


# initialiation de la lampe
## get the energy balance
EnergyBalance = int(client.call(_from=param['pine2']['address'], to=param['contract']['address'],
                                data=param['contract']['fctEnergyBalance'], block="latest"), 0)
print('EnergyBalance = ' + str(EnergyBalance))

if EnergyBalance >= param['pine2']['limit'] :
    # on allume la lampe
    turnRelay("4")
    lampStatus = int(ser.read())

time0 = getDateTime(pineURL, data, headers)


while 1:
    # delay to define
    time.sleep(20)

    # récupération de l'énergie consommée ou produite
    time1 = getDateTime(pineURL, data, headers)
    sumWatt = getEnergySum(pineURL, data, headers, time0, time1)

    print('time : ' + time.strftime("%D %H:%M:%S", time.localtime(int(time1))) + ', sumWatt = ' + str(sumWatt))

    time0 = time1

    if sumWatt !=0 :

        # Consumer
        if param[pine]['typ'] == 'C':

            # to update Energy balance (consumer)
            hashData = param['contract']['fctConsumeEnergy'] + padhexa(hex(sumWatt))
            # DEBUG : using pine2 directly for test and debug
            response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)

            # get the energy balance
            EnergyBalance = int(client.call(_from=param['pine2']['address'], to=param['contract']['address'], data=param['contract']['fctEnergyBalance'], block="latest"), 0)
            print('EnergyBalance = ' + str(EnergyBalance))

            # if energy balance is too low, a energy transaction is triggered
            if EnergyBalance < param['pine2']['limit']:
                print(lampStatus)
                if lampStatus == 1:
                    turnRelay("4")
                    lampStatus = int(ser.read())
                watt = 350 # to adjust
                seller = param['pine1']['address'].replace('0x', '')
                hashData = param['contract']['fctBuyEnergy'] + padaddress(seller) + padhexa(hex(watt))
                response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)
                time.sleep(2)
                turnRelay("4")
                lampStatus = int(ser.read())
                print(lampStatus)

        # Producer
        else:
            # to update Energy balance (producer)
            hashData = param['contract']['fctSetProduction'] + padhexa(hex(sumWatt))
            response = client.send_transaction(_from=param['pine2']['address'], to=param['contract']['address'], data=hashData)
