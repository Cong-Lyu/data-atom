import json
import requests as req
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import time
import hashlib
from sentence_transformers import SentenceTransformer

##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntologyList = {'DomainOnto01': 'City_Visibility', 'DomainOnto02': 'City_Wind_Speed', 'DomainOnto03': 'City_AirPollution_Level', 'DomainOnto04': 'City_Aviation_Hazards'}
## specified by agents
OperationalOntologyList = {'OperOnto01': 'City_Tokyo', 'OperOnto02': 'City_Shirahama', 'OperOnto03': 'Climate_East_Asia', 'OperOnto04': 'Cultural_Event_Effects', 'OperOnto05': 'City_Osaka', 'OperOnto06': 'City_Kyoto'}
AuthoritativeOntologyList = {'AuthOnto01': 'JP_PoliceStation', 'AuthOnto02': 'JP_MeteorologyStation', 'AuthOnto03': 'JP_Transport', 'AuthOnto04': 'JP_PublicBroadCast'}
## private_1 ---->  JP_MeteorologyStation,  private_2 -------> JP_Transport, private_3 -----> JP_PublicBroadCast
PrivateOntologyList = {'PrivateOnto01': 'Research_Use_Only', 'PrivateOnto02': 'Commercial_Use_Allowed', 'PrivateOnto03': 'Secret_Data', 'PrivateOnto04': 'Public_Broadcast'}
##rules policies,
ontologyPointers = ['PrivateOnto04']


if __name__ == '__main__':
    ##------------------------------------------data fetch------------------------------------##
    apiKey = 'bb61f1bb3b03d9e9b34e982395cbf3ab'
    cityName = 'Tokyo'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={cityName}&appid={apiKey}'
    fields = ['visibility', 'coord', 'wind', 'clouds']
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

    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedWeatherData']
    collection = db['data']


    ##-----------------------------------fields selection--------------------------------##
    jsonData = {}
    jsonData[fields[0]] = data[fields[0]]   ##try only visibility first
    # jsonData = {}
    # for i in range(len(fields)):
    #     jsonData[fields[i]] = data[fields[i]]
    # print(jsonData)
    dataString = json.dumps(jsonData)
    dataBytes = dataString.encode()
    # print(len(dataBytes))  ## to check if the length of the dataBytes exceeds 190, if exceeds, probably cannot use asymmetric encryption directly.


    ##-----------------------------------------symmetric encryption----------------------------------------##
    symmetricKey = Fernet.generate_key()       ##generate a random symmetric key
    print("This is the symmetric key:", symmetricKey)
    fernet = Fernet(symmetricKey)
    cipherText = fernet.encrypt(dataBytes)       ##Encrypt the sensitive data
    print('\nThis is the encrypted data:', cipherText)


    ##-------------------------------------data signing and sealing (exclusive rights token & access token)-----------------------------------##
    exclusiveToken = ''    ##Only the Meteorology Station has the exclusive right.
    hashDiction = {}       ##Agents token dictionary
    for i in range(1, 4):
        with open("asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
        encryptedSymKey = publicKey.encrypt(
            symmetricKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        publicKeyBytes = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
        hashDiction[hashedPublicKey] = encryptedSymKey
        if i == 1:
            exclusiveToken = hashedPublicKey
        # print('\nThis is the encrypted symmetric key:', encryptedSymKey




    ##------------------------------------Ontology Latching--------------------------------------##
    key = fields[0]       ##key used for machine learning
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = [key]
    i = 1
    while 'DomainOnto0{0}'.format(i) in DomainOntologyList:          ##Including all other Domain Ontologies
        sentences.append(DomainOntologyList['DomainOnto0{0}'.format(i)])
        i += 1
    print('those are the sentences:', sentences, '\n')
    embedding = model.encode(sentences)
    similarities = model.similarity(embedding, embedding)
    print('let us look at the similarity result: ', similarities, '\n')

    most_related_Index = 1      ##find the most relevant Domain Ontology with for loop
    for i in range(2, 5):
        if similarities[0][i] > similarities[0][most_related_Index]:
            most_related_Index = i
    most_relevant_DomainOnto = 'DomainOnto0{0}'.format(most_related_Index)

    ontologyPointers.append(most_relevant_DomainOnto)    ##put the most relevant one into the ontology pointer list



    ##------------------------------------Atom Assemble-------------------------------------##
    Wrapper = {
               'Exclusive Rights Token': exclusiveToken,
               'Access Tokens': hashDiction,
               'Authority Pointer': ['AuthOnto02', 'AuthOnto03'],
               'Ontology Pointers': ontologyPointers
               }
    Nucleus = {'encryptedData': cipherText}
    collection.insert_one({'Wrapper' : Wrapper, 'Nucleus' : Nucleus})



    ##-----------------------------------Verification----------------------------------------##
    with open("asymKeys/public_1.pem", 'rb') as f:
        publicKey = serialization.load_pem_public_key(f.read())
    publicKeyBytes = publicKey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
    print('This is the hashed public key for user 1: ', hashedPublicKey, '\n', 'This is his encrypted sym key: ',  hashDiction[hashedPublicKey])



