from pymongo import MongoClient
from bson import ObjectId
import hashlib
import time
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import textwrap

def consumptionContextGenerator(db):
    csc = {}
    ##-----------------------------------context--------------------------------------##
    timeStamp = time.time()
    context = {
        'timeStamp' : timeStamp
    }


    ##----------------------------------agent ascertain---------------------------------##
    agentPublicKeys = {}
    for i in range(1, 4):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
            agentPublicKeys['agent{0}'.format(i)] = publicKey


    ##-----------------------------------leash ticket---------------------------------------##
    leashTicketId = '6a968597b9b3988586fdf6a5'   ##get the leash ticket
    leashTicket = db['data'].find_one({"_id": ObjectId(leashTicketId)})

    csc['context'] = context
    csc['leashTicket'] = leashTicket
    csc['agents'] = agentPublicKeys

    return csc



if __name__ == '__main__':
    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']

    ##-----------------------------------------conception context obtaining---------------------------------##
    csc = consumptionContextGenerator(db)
    print('this is the consumption context: ', csc, '\n')

    ##------------------------------------------Atoms obtaining based on Leash Ticket------------------------------------##
    atomsList = []
    for item in csc['leashTicket']['leashedAtoms']:
        atomsList.append(csc['leashTicket']['leashedAtoms'][item]['Id'])
    print('These are the atoms included in the leash ticket:', atomsList, '\n')


    ##-----------------------------------Access Check------------------------------------##
    WAM = np.zeros((len(csc['agents']), len(atomsList)))
    RAM = np.zeros((len(csc['agents']), len(atomsList)))
    # print('\n', WAM, '\n\n', RAM, '\n\n')

    agentNo = 1
    for i in csc['agents'].items():
        publicKeyBytes = i[1].public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()

        atomNo = 1
        for j in atomsList:
            atom = db['data'].find_one({'_id': ObjectId(j)})
            isWriteAccess = 0
            ##--------------------------------check if this agent's public key matches one of the tokens in the wrapper-----------------------------------##
            for item in atom['Wrapper']['Access Tokens'].items():
                isWriteAccess = isWriteAccess + 1
                # print('\nThis is the hashed public key: ', item[0])
                if (hashedPublicKey == item[0] and isWriteAccess == 1):
                    WAM[agentNo - 1, atomNo - 1] = 1
                    break
                elif hashedPublicKey == item[0] and isWriteAccess != 1:
                    RAM[agentNo - 1, atomNo - 1] = 1
                    break
            atomNo += 1
        agentNo += 1
    print('This is the WAM: \n', WAM, '\n\n', 'This is the RAM: \n', RAM)

    #---------------------------------------------BM generation---------------------------------------##
    BM = np.zeros((len(csc['agents']), len(atomsList)))
    for i in range(WAM.shape[0]):
        for j in range(WAM.shape[1]):
            if(WAM[i, j] == 1 or RAM[i, j] == 1):
                BM[i, j] = 1

    print('\nThis is the BM: \n', BM)

    acceptedAtom = []
    for i in range(len(atomsList)):
        isAccepted = True
        for j in range(BM.shape[0]):
            if BM[j, i] == 0:
                isAccepted = False
        if isAccepted:
            acceptedAtom.append(atomsList[i])

    print('\nThose are the accepted atoms', acceptedAtom)


    ##------------------------------------Atom Decryption-------------------------------------##
    ##-------------------------------------obtain all hashed public key------------------------------##
    hashedPublicKeyList = []
    privateKeyList = []
    for i in range(len(csc['agents'])):
        with open("../asymKeys/private_{0}.pem".format(i + 1), 'rb') as f:  ##obtain the saved public key
            privateKey = serialization.load_pem_private_key(f.read(), password=None)
        with open("../asymKeys/public_{0}.pem".format(i + 1), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
        publicKeyBytes = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
        hashedPublicKeyList.append(hashedPublicKey)
        privateKeyList.append(privateKey)

    # print(hashedPublicKeyList, privateKeyList)
    for item in acceptedAtom:
        atom = db['data'].find_one({"_id": ObjectId(item)})
        print('Now we are processing: ', atom, '\n')
        for i in range(len(hashedPublicKeyList)):
            ##------------------------find the token for this agent, so that we can get his encrypted Symmetric Key--------------------##
            for j in atom['Wrapper']['Access Tokens'].items():
                if hashedPublicKeyList[i] == j[0]:
                    print('This is the hashed public key: ', hashedPublicKeyList[i], '\nThis is the hashed public key: ', j[0])
                    symmetricKey = privateKeyList[i].decrypt(
                        j[1],
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    fernet = Fernet(symmetricKey)
                    data = fernet.decrypt(atom['Nucleus']['encryptedData'])
                    print('This is the encrypted data in the atom: \n', textwrap.fill(data.decode(), width=100), '\n')
                    break






