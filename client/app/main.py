import requests

CONTROLLER_IP = "192.168.1.1"
NAME = "MATHEWCLIENT1"

def fetchClientPublicKey():
    publicKey = "invalid"
    with open('publickey', 'r') as f:
        publicKey = f.readline().rstrip('\n')
    return publicKey


def connectToController():
    API_KEY = input("enter API key - ")
    
    url = f"http://{CONTROLLER_IP}:5000/register"
    headers = {"weaver-auth": API_KEY}
    payload = {
        "publicKey": fetchClientPublicKey(),
        "name": NAME
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"{response.json()['error']}.....exiting")
        return -1
    
    controllerPublicKey = response.json()['controllerPublicKey']
    allocatedIP = response.json()['allocatedIP']

    return 0
    
    



if __name__ == '__main__':
    connectToController()
