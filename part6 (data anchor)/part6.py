from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import hashlib
from sentence_transformers import SentenceTransformer
import time
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text
import copy

##-----------------------------------------Ontology Selection----------------------------------------------##
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

OperationalOntology = {
    'Geographic': {'node1': 'abc', 'node2': 'abc'},
    'Cultural': {'node1': 'abc', 'node2': 'abc'},
    'Ethnic': {'node1': 'abc', 'node2': 'abc'}
}

AuthoritativeOntology = {
    'RoyalHospital': {
        'ChainOfCommand': {'node1': 'abc', 'node2': 'abc'},
        'AuthorityStructures': {'node1': 'abc', 'node2': 'abc'}
    }
}

PrivateOntology = {
    'Mark': {
        'Id': '1',
        'Accessibility': ['doctors are granted full access', 'family members are granted full access'],
        'Deniability': ['friends have no access']
    },
    'Dr.Smith': {
        'Id': '2',
        'Accessibility': ['other doctors who look after the same patient are granted access', 'Nurses on duty are granted access'],
        'Deniability': ['doctors not belong to royal hospital do not have access']
    }
}

def conceptionContextGenerator():
    ccc = {}
    ##-----------------------------------context--------------------------------------##
    timeStamp = time.time()
    context = {
        'location' : 'Unknown',
        'timeStamp' : timeStamp
    }


    ##----------------------------------agent ascertain---------------------------------##
    involvedAgents = []
    for i in range(1, 4):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
        involvedAgents.append({
            # 'agentAuthorityPointer': 'AuthOnto{0}'.format(i),
            'publicKey': publicKey
        })


    ##-----------------------------------ontology base-------------------------------------##
    ontology = {
        'DomainOntology': ['Asthma', 'AnalWarts'],
        'OperationalOntology': [],
        'PrivateOntology': ['Mark', 'Dr.Smith']
    }


    ccc['context'] = context
    ccc['agents'] = involvedAgents
    ccc['ontology'] = ontology
    return ccc



if __name__ == '__main__':
    ##-----------------------------------------conception context obtaining---------------------------------##
    ccc = conceptionContextGenerator()
    print('this is the conception context: ', ccc)
    ontologyPointers = []


    ##------------------------------------------data obtaining------------------------------------##
    list1 = []   ## prepare for topics extraction
    data = ''   ## the data to be encrypted
    for i in range(20):
        with open("article{0}.txt".format(i + 1), "r", encoding='utf-8') as file:
            temp1 = file.read()
        data += temp1
        list1.append(temp1)
    # print("This is data:", data)


    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']



    ##-----------------------------------keywords obtain------------------------------------##  how many anchors are there
    hdbscanModel = HDBSCAN(
        min_cluster_size=2, min_samples=1
    )

    interestedStopWords = list(text.ENGLISH_STOP_WORDS.union(
        {'patient', 'doctor', 'yes', 'okay', 'right', 'brother', 'did', 'do', 'does', 'like', 'yeah', 'know', 'good', 'order', 'thats', 'ago', 'wow', 'taking'
         , 'think', 'long', 'oh', 'july', 'correct', 'day', 'im', 'didnt', 'having', 'dont', 'dose', 'old', 'felt', 'amazing', 'dad', 'problem', 'today', 'let'
        , 'food', 'just'
         }
    ))

    vectorizerModel = CountVectorizer(stop_words = interestedStopWords)   ##setting stop words

    topicModel = BERTopic(hdbscan_model = hdbscanModel, vectorizer_model = vectorizerModel)

    topic, probs = topicModel.fit_transform(list1)
    print(topic)
    print(max(topic))

    for i in range(max(topic) + 1):
        print(topicModel.get_topic(i))

    print(topicModel.get_topic(i)[0])
    print(topicModel.get_topic(i)[0][0])

    keywords = []
    keywordsNum = 0
    for i in range(max(topic) + 1):
        for j in range(len(topicModel.get_topic(i))):
            keywords.append(topicModel.get_topic(i)[j][0])
            keywordsNum += 1



    ##-----------------------------------------symmetric encryption----------------------------------------##
    dataBytes = data.encode()
    symmetricKey = Fernet.generate_key()       ##generate a random symmetric key
    print("This is the symmetric key:", symmetricKey)
    fernet = Fernet(symmetricKey)
    cipherText = fernet.encrypt(dataBytes)       ##Encrypt the sensitive data
    print('\nThis is the encrypted data:', cipherText)




    ##-------------------------------------data signing and sealing (exclusive rights token & access token)-----------------------------------##
    exclusiveToken = ''    ##Only the WHO has the exclusive right.
    hashDiction = {}       ##Agents token dictionary
    for i in range(1, 4):
        ##--------------------------obtain the public key from the conception context instead-----------------------##
        publicKey = ccc['agents'][i - 1]['publicKey']
        print('publicKey: ', publicKey)

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
            exclusiveToken = hashedPublicKey  ##exclusive token generation
        # print('\nThis is the encrypted symmetric key:', encryptedSymKey




    ##------------------------------------Ontology Latching--------------------------------------##
    print(ccc['ontology'])
    print(ccc['ontology']['DomainOntology'])

    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i])


    for i in ccc['ontology']['DomainOntology']:
        nodesNum = 0
        sen = copy.deepcopy(sentences)
        for j in DomainOntology[i].items():
            if(j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    sen.append(k['Name'])
                    nodesNum += 1

        print(sen)


        print('those are the sentences:', sen, '\n')
        embedding = model.encode(sen)
        similarities = model.similarity(embedding, embedding)
        print('let us look at the similarity result: ', similarities, '\n')




        ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
        posi = (0, 0)    ##find the most relevant Domain Ontology with for loop
        value = 0
        for m in range(0, keywordsNum):
            for n in range(keywordsNum, keywordsNum + nodesNum):
                if similarities[m][n] > value:
                    value = similarities[m][n]
                    posi = [m, n]
        print(posi)
        print(similarities[posi[0]][posi[1]])
        print(sen[posi[1]])


        print(DomainOntology[i]['Id'])
        pointer = {}
        found = 0
        for j in DomainOntology[i].items():
            if(j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                for k in j[1]:
                    if k['Name'] == sen[posi[1]]:
                        pointer[DomainOntology[i]['Id']] = k['Id']
                        found = 1
                        break
            if found:
                break

        ontologyPointers.append(pointer)

    print(ontologyPointers)




    ##------------------------------------Atom Assemble-------------------------------------##
    Wrapper = {
           'Exclusive Rights Token': exclusiveToken,
           'Access Tokens': hashDiction,
           'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
           'Ontology Pointers': ontologyPointers
           }
    Nucleus = {'encryptedData': cipherText}
    atom1 = collection.insert_one({'Wrapper' : Wrapper, 'Nucleus' : Nucleus})




    ##-----------------------------------leash ticket---------------------------------------##
    leashTicket = {
        'leashedAtoms': {
            'Atom1': {
                'Id': str(atom1.inserted_id),
                'Type': 'DataAtom',
            },
            'Atom2': {
                'Id': '6a421a637137da02587894cd',
                'Type': 'DataAtom',
            }
        }
    }
    collection.insert_one(leashTicket)