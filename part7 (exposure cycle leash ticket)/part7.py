from pymongo import MongoClient
from bson import ObjectId
from cryptography.hazmat.primitives import serialization
import hashlib
import time
import numpy as np

def consumptionContextGenerator(db):
    csc = {}
    ##-----------------------------------context--------------------------------------##
    timeStamp = time.time()
    context = {
        'location' : 'Unknown',
        'timeStamp' : timeStamp
    }


    ##----------------------------------agent ascertain---------------------------------##
    agentPublicKeys = {}
    for i in range(1, 5):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
            agentPublicKeys['agent{0}'.format(i)] = publicKey




    ##-----------------------------------query-------------------------------------##
    ##query comes in here




    ##-----------------------------------leash ticket---------------------------------------##
    leashTicketId = '6a421f3e77defcef82430ecf'   ##get the leash ticket
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
    ##-----------------------------------Access tokens-------------------------------------##
    WAM = np.zeros((4, 2))
    RAM = np.zeros((4, 2))
    print('\n', WAM, '\n\n', RAM, '\n\n')

    agentNo = 1
    for i in csc['agents'].items():
        print('This is the agent: ', i[0])
        print('This is his public key: ', i[1])
        publicKeyBytes = i[1].public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
        print('This is his hashed public key: ', hashedPublicKey)

        atomNo = 1
        for j in atomsList:
            atom = db['data'].find_one({'_id': ObjectId(j)})
            # print('This is the atom: ', atom['Wrapper']['Access Tokens'])
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

    print('\n\nThis is the WAM: \n', WAM, '\n\n', 'This is the RAM: \n', RAM)

    #---------------------------------------------BM generation---------------------------------------##
    BM = np.zeros((4, 2))
    for i in range(WAM.shape[0]):
        for j in range(WAM.shape[1]):
            if(WAM[i, j] == 1 or RAM[i, j] == 1):
                BM[i, j] = 1

    print('\nThis is the BM: \n', BM)



    # ##------------------------------------Atom Decryption-------------------------------------##
    # for item in accessDescription.items():
    #     print('Now we are processing: ', item[0], item[0][-3])
    #     with open("../asymKeys/private_{0}.pem".format(item[0][-3]), 'rb') as f:  ##obtain the saved public key
    #         privateKey = serialization.load_pem_private_key(f.read(), password = None)
    #     with open("../asymKeys/public_{0}.pem".format(item[0][-3]), 'rb') as f:  ##obtain the saved public key
    #         publicKey = serialization.load_pem_public_key(f.read())
    #     publicKeyBytes = publicKey.public_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PublicFormat.SubjectPublicKeyInfo)
    #     hashedPublicKey = hashlib.sha256(publicKeyBytes).hexdigest()
    #
    #
    #     ##----------------------------decrypt every atom that this agent has access to-----------------------------------##
    #     for atomId in item[1]:
    #         atom = db['data'].find_one({"_id": ObjectId(atomId)})
    #
    #
    #         ##------------------------looping to find the token for this agent, so that we can get his encrypted Symmetric Key--------------------##
    #         for j in atom['Wrapper']['Access Tokens'].items():
    #             if (hashedPublicKey == j[0]):
    #                 print('This is the hashed public key: ', j[0])
    #                 symmetricKey = privateKey.decrypt(
    #                     j[1],
    #                     padding.OAEP(
    #                         mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #                         algorithm=hashes.SHA256(),
    #                         label=None
    #                     )
    #                 )
    #
    #                 fernet = Fernet(symmetricKey)
    #                 data = fernet.decrypt(atom['Nucleus']['encryptedData'])
    #                 print('This is the encrypted data in the atom: ', data, '\n')
    #                 break






