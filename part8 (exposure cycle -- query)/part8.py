from pymongo import MongoClient
from bson import ObjectId
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib
import time
import numpy as np
import spacy
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import copy

from part1.main import ontologyPointers

DomainOntology = {
    'Asthma': {
        'Id': '11',
        'Parent': [
            {
                'Id': '21215431316',
                'Name': 'Disorder of respiratory system'
            }
        ],
        'Children': [
            {
                'Id': '21256751316',
                'Name': 'Asthma in pregnancy'
            },
            {
                'Id': '29865431316',
                'Name': 'Childhood asthma'
            }
        ],
        'Symptoms': [
            {
                'Id': '29865431316a',
                'Name': 'Shortness of breath'
            },
            {
                'Id': '29865431316b',
                'Name': 'Chest tightness'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431316c',
                'Name': 'Methacholine challenge'
            },
            {
                'Id': '29865431316d',
                'Name': 'Imaging tests'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431316e',
                'Name': 'Inhaled corticosteroids'
            },
            {
                'Id': '29865431316f',
                'Name': 'Leukotriene modifiers'
            }
        ]
    },
    'AnalWarts': {
        'Id': '2212112',
        'Parent': [
            {
                'Id': '212112456',
                'Name': 'Anal Infection'
            }
        ],
        'Children': [],
        'Symptoms': [
            {
                'Id': '29865431316A',
                'Name': 'Bleeding with sex'
            },
            {
                'Id': '29865431316B',
                'Name': 'A cauliflower-like shape caused by a few warts close together'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431316C',
                'Name': 'Pap tests'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431316D',
                'Name': 'Imiquimod'
            },
            {
                'Id': '29865431316E',
                'Name': 'Trichloroacetic acid'
            }
        ]
    }
}


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
    query = 'We would like to obtain the dialogue between Doctor Smith and his Patient Mark about his symptoms.'



    ##-----------------------------------leash ticket---------------------------------------##
    # leashTicketId = '6a421f3e77defcef82430ecf'   ##get the leash ticket
    # leashTicket = db['data'].find_one({"_id": ObjectId(leashTicketId)})

    csc['context'] = context
    # csc['leashTicket'] = leashTicket
    csc['agents'] = agentPublicKeys
    csc['query'] = query

    return csc



if __name__ == '__main__':
    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']



    ##-----------------------------------------conception context obtaining---------------------------------##
    csc = consumptionContextGenerator(db)
    print('this is the consumption context: ', csc, '\n')




    ##------------------------------------------Query Decoding------------------------------------##
    ontologyPointers = []

    kbModel = KeyBERT()
    keywords = kbModel.extract_keywords(
        csc['query'],
        stop_words='english',
        use_mmr=True  ## exclude those similar words, such as apple and apples
    )
    print('keywords: ', keywords)
    keywordsNum = len(keywords)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i][0])

    ontologies = ['Asthma', 'AnalWarts']
    for i in ontologies:
        nodesNum  = 0
        sen = copy.deepcopy(sentences)
        for j in DomainOntology[i].items():
            if(j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    sen.append(k['Name'])
                    nodesNum += 1


        print('those are the sentences:', sen, '\n')
        embedding = model.encode(sen)
        relevanceResult = model.similarity(embedding, embedding)
        print('let us look at the relevance result: ', relevanceResult, '\n')


        ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
        posi = (0, 0)  ##find the most relevant Domain Ontology with for loop
        value = 0
        for m in range(0, keywordsNum):
            for n in range(keywordsNum, keywordsNum + nodesNum):
                if relevanceResult[m][n] > value:
                    value = relevanceResult[m][n]
                    posi = [m, n]
        print(posi)
        print(relevanceResult[posi[0]][posi[1]])
        print(sen[posi[1]])


        print(DomainOntology[i]['Id'])
        pointer = {}
        found = 0
        for j in DomainOntology[i].items():
            if (j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    if k['Name'] == sen[posi[1]]:
                        pointer[DomainOntology[i]['Id']] = k['Id']
                        found = 1
                        break
            if found:
                break

        ontologyPointers.append(pointer)

    print(ontologyPointers)


    # ##-------------------------------------hookstack construction-------------------------------------------##
    # hookStack = {'stack': []}
    #
    # for i in range(len(keywords)):
    #     temp = 0 ##the most similar ontology
    #     posi = [] ## the position of the most similar ontology
    #     for j in range(len(keywords), relevanceResult.shape[1]):
    #         if(relevanceResult[i, j] > temp):
    #             temp = relevanceResult[i, j]
    #             posi = [i, j]
    #     print(temp)
    #     print(posi)
    #
    #     hookStack['stack'].append({'segment1': i + 1, 'keyword': keywords[i][0], 'mostSimilarOnto': 'DomainOnto{0}'.format(posi[1] - len(keywords) + 1)})
    #
    # print(hookStack)



    ##------------------------------------obtain candidates-----------------------------------##
    candidates = []
    for i in ontologyPointers:
        for item in collection.find():
            if 'Wrapper' in item:
                for j in item['Wrapper']['Ontology Pointers']:
                    if (j == i) and (item['_id'] not in candidates):
                        candidates.append(item['_id'])

    print('Those are the candidates: ', candidates)



    #-----------------------------------Access Check------------------------------------##
    #-----------------------------------Access tokens-------------------------------------##
    WAM = np.zeros((len(csc['agents']), len(candidates)))
    RAM = np.zeros((len(csc['agents']), len(candidates)))
    # print('\n', WAM, '\n\n', RAM, '\n\n')

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
        for j in candidates:
            atom = db['data'].find_one({'_id': j})
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
    BM = np.zeros((len(csc['agents']), len(candidates)))
    for i in range(WAM.shape[0]):
        for j in range(WAM.shape[1]):
            if(WAM[i, j] == 1 or RAM[i, j] == 1):
                BM[i, j] = 1

    print('\nThis is the BM: \n', BM)



    ##-----------------------------atom filtering-----------------------------------##
    acceptedAtoms = []
    for i in range(BM.shape[1]):
        isAccepted = True
        for j in range(BM.shape[0]):
            if BM[j, i] == 0:
                isAccepted = False
        if isAccepted:
            acceptedAtoms.append(i)  ##BM's column represents all the candidates.

    print('Those are accepted atoms: ', acceptedAtoms)





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






