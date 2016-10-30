import json
import requests
import time

from eth_rpc_client import Client

client = Client(host="127.0.0.1", port="8545")

def padhexa(s):
    return s[2:].zfill(64)


def getEnergySum(t0, t1):
    sumEnergy = 0
    headers = {'Content-Type': 'application/json', }
    data = 'login=debian&password=debian'

    result = requests.post('http://192.168.0.34:8080/api/4/get/watts/by_time/' + str(t0) + '/' + str(t1),
                           headers=headers, data=data)
    parsed_json = json.loads(result.text)
    print('=> 1 = ' + str(parsed_json['data']))

    for n in range(0, len(parsed_json['data'])):
        watt = int(parsed_json['data'][n]['value'])
        print('=> 2 = ' + str(parsed_json['data'][n]['value']))       
        sumEnergy = sumEnergy + watt

    return sumEnergy


def getDateTime():
        headers = {'Content-Type': 'application/json',}
        data = 'login=debian&password=debian'

        result = requests.post('http://192.168.0.34:8080/api/time',
                               headers=headers, data=data)
        parsed_json = json.loads(result.text)
        return parsed_json['data']


# adresse du contract DAISEE deploye sur la BC
contractAddress = '0x124f1fb67f450bd3234ec0e12d519fa61e6bc543'

# parametres des PINE => a mettre dans un fichier parametre
# pour ce proto, il y a 2 producteurs d'energie ('P') et 1 consommateur ('C')
pine1 = {'address': '0x520f9b737b97a52945075dbf393d29adca000cca', 'url': 'http://192.168.0.34:8080', 'typ': 'C'}
pine2 = {'address': '0x98181b49bf309364fba5d75ff57d30509b2a24fd', 'url': 'http://192.168.0.29:8080', 'typ': 'P'}
pine3 = {'address': '0x8915cf74dff23cbca59f356317098d4cf3d47203', 'url': 'http://192.168.0.xx:8080', 'typ': 'P'}

# definition du pine => a mettre dans un fichier parametre
pine = pine1

time0 = getDateTime()

while 1:
    print('1. dbt boucle')

    # delai a definir
    time.sleep(20)
    time1 = getDateTime()

    sumWatt = getEnergySum(time0, time1)
    time0 = time1
    print('sumWatt = ' + str(sumWatt))

    print('2. apres somme energie')

    # le PINE est un consommateur
    if pine['typ'] == 'C':
        print('conso')
        # execution de la fonction consumeEnergy
        hashConsumeEnergy = "298d65a1"
        print('sumWatt = ' + str(sumWatt))
        print('padhexa(hex(sumWatt)) = ' + str(padhexa(hex(sumWatt))))
        hashData = hashConsumeEnergy + padhexa(hex(sumWatt))
        response = client.send_transaction(_from=pine['address'], to=contractAddress, data=hashData)
        print("hash Transaction= " + response)


    # le PINE est un producteur
    else :
        print('producteur')
        # execution de la fonction setProduction
        hashSetProduction = "567cc2b6"
        hashData = hashSetProduction + padhexa(hex(sumWatt))
        response = client.send_transaction(_from=pine['address'], to=contractAddress, data=hashData)
        print("hash Transaction= " + response)

