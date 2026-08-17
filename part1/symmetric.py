import base64
import json
import requests as req
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import time

if __name__ == '__main__':
    apiKey = 'bb61f1bb3b03d9e9b34e982395cbf3ab'
    cityName = 'Tokyo'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={cityName}&appid={apiKey}'

    response = req.get(url)   ##fetch data and transfer it into dictionary
    data = response.json()
    print("This is data:", data)

    # privateKey = rsa.generate_private_key(
    #     public_exponent=65537,
    #     key_size=2048
    # )
    #
    # publicKey = privateKey.public_key()
    # print(
    #     privateKey.private_bytes(encoding=serialization.Encoding.PEM,
    #                              format=serialization.PrivateFormat.TraditionalOpenSSL.PKCS8,
    #                              encryption_algorithm=serialization.NoEncryption()).decode(),
    #     publicKey.public_bytes(encoding=serialization.Encoding.PEM,
    #                            format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    # )

    with open("asymKeys/public_1.pem", 'rb') as f:   ##obtain the saved public key
        publicKey = serialization.load_pem_public_key(f.read())
    selectedData = {'visibility': data['visibility'],
                    'dt': data['dt'],
                    'coord': data['coord'],
                    'wind' : data['wind'],
                    'clouds' : data['clouds']
                    }
    dataString = json.dumps(selectedData)
    dataBytes = dataString.encode()


    symmetricKey = Fernet.generate_key()
    print("This is the symmetric key:", symmetricKey)
    fernet = Fernet(symmetricKey)
    cipherText = fernet.encrypt(dataBytes)
    print('\nThis is the encrypted data:', cipherText)

    encryptedSymKey = publicKey.encrypt(
        symmetricKey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print('\nThis is the encrypted symmetric key:', encryptedSymKey)


    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedWeatherData']
    collection = db['data']
    collection.insert_one({'timeStamp': time.time(), 'sourceId': 1, 'encryptedData': cipherText})


    doc = collection.find_one()   ##get the encrypted text out for comparison.
    encryptedData = doc['encryptedData']
    print("\nThis is the encrypted data saved in the database:", encryptedData)


    with open("asymKeys/private_1.pem", 'rb') as f:   ##obtain the private key
        privateKey = serialization.load_pem_private_key(f.read(), password = None)
    decrptedSymKey = privateKey.decrypt(
        encryptedSymKey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print('\nThis is the decrypted symmetric key:', decrptedSymKey)


    ##https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html