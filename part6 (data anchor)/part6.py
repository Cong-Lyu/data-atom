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
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import copy

##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntology = {
    'Asthma': {
        'Id': 'A1',
        'Parent': [
            {
                'Id': '21215431311A',
                'Name': 'Disorder of respiratory system'
            }
        ],
        'Children': [
            {
                'Id': '21256751312A',
                'Name': 'Asthma in pregnancy'
            },
            {
                'Id': '29865431313A',
                'Name': 'Childhood asthma'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S1',
                'Name': 'Shortness of breath'
            },
            {
                'Id': 'S2',
                'Name': 'Chest tightness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D1',
                'Name': 'Methacholine challenge'
            },
            {
                'Id': 'D2',
                'Name': 'Imaging tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T1',
                'Name': 'Inhaled corticosteroids'
            },
            {
                'Id': 'T2',
                'Name': 'Leukotriene modifiers'
            }
        ]
    },
    'AnalWarts': {
        'Id': 'A2',
        'Parent': [
            {
                'Id': '212112410B',
                'Name': 'Anal Infection'
            }
        ],
        'Children': [],
        'Symptoms': [
            {
                'Id': 'S3',
                'Name': 'Bleeding with sex'
            },
            {
                'Id': 'S4',
                'Name': 'A cauliflower-like shape caused by a few warts close together'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D3',
                'Name': 'Pap tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T3',
                'Name': 'Imiquimod'
            },
            {
                'Id': 'T4',
                'Name': 'Trichloroacetic acid'
            }
        ]
    },
    'Heart block': {
        'Id': 'A3',
        'Parent': [
            {
                'Id': '212112410a',
                'Name': 'Conduction disorder of the heart'
            }
        ],
        'Children': [
            {
                'Id': '212112411a',
                'Name': 'Atrioventricular block'
            },
            {
                'Id': '212112412a',
                'Name': 'Heart block caused by drug'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S5',
                'Name': 'fainting (syncope)'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D4',
                'Name': 'Electrocardiogram (ECG or EKG)'
            }
        ],
        'Treatment': [
            {
                'Id': 'T5',
                'Name': 'medications to reduce high blood pressure or reduce symptoms of heart failure'
            }
        ]
    },
    'Pneumonia': {
        'Id': 'A4',
        'Parent': [
            {
                'Id': '212112410b',
                'Name': 'Infectious disease of lung (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410b',
                'Name': ' Abscess of lung with pneumonia (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S6',
                'Name': 'Chest pain when you breathe or cough'
            },
            {
                'Id': 'S7',
                'Name': 'Fever, sweating and shaking chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D5',
                'Name': 'Blood tests'
            }
        ],
        'Treatment': [
            {
                'Id': 'T6',
                'Name': 'Antibiotics'
            },
            {
                'Id': 'T7',
                'Name': 'Cough medicine'
            }
        ]
    },
    'Bronchitis': {
        'Id': 'A5',
        'Parent': [
            {
                'Id': '212182410c',
                'Name': 'Inflammation of specific body organs'
            }
        ],
        'Children': [
            {
                'Id': '212112410c',
                'Name': 'Acute bronchitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S8',
                'Name': 'Sore throat'
            },
            {
                'Id': 'S9',
                'Name': 'Slight fever and chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D6',
                'Name': 'Chest X-ray'
            }
        ],
        'Treatment': [
            {
                'Id': 'T8',
                'Name': 'Cough medicine'
            },
            {
                'Id': 'T9',
                'Name': 'Antibiotics'
            }
        ]
    },
    'Tuberculosis': {
        'Id': 'A6',
        'Parent': [
            {
                'Id': '212112410d',
                'Name': 'Disorder characterized by granuloma formation (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112411d',
                'Name': 'Acute tuberculous ulcer (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S10',
                'Name': 'Low fever'
            },
            {
                'Id': 'S11',
                'Name': 'Tiredness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D7',
                'Name': 'Listening to breathe with a stethoscope'
            }
        ],
        'Treatment': [
            {
                'Id': 'T10',
                'Name': 'Isoniazid'
            },
            {
                'Id': 'T11',
                'Name': 'Rifampin'
            }
        ]
    },
    'Gastritis': {
        'Id': 'A7',
        'Parent': [
            {
                'Id': '212112410e',
                'Name': 'Disorder of stomach (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '2121124111e',
                'Name': 'Acute gastritis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S12',
                'Name': 'Vomiting'
            },
            {
                'Id': 'S13',
                'Name': 'Nausea'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D8',
                'Name': 'Tests for H. pylori'
            }
        ],
        'Treatment': [
            {
                'Id': 'T12',
                'Name': 'Antibiotics to kill H. pylori'
            },
            {
                'Id': 'T13',
                'Name': 'Medicines that block acid production and promote healing'
            }
        ]
    },
    'Hepatitis A': {
        'Id': 'A8',
        'Parent': [
            {
                'Id': '212112410f',
                'Name': 'Viral hepatitis (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410f',
                'Name': 'Acute type A viral hepatitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S14',
                'Name': 'Unusual tiredness and weakness'
            },
            {
                'Id': 'S39',
                'Name': 'Sudden nausea and vomiting and diarrhea'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D9',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': 'T14',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': 'T15',
                'Name': 'Avoid alcohol and use medications with care'
            }
        ]
    },
    'Cataracts': {
        'Id': 'A9',
        'Parent': [
            {
                'Id': '212112410j',
                'Name': 'Degenerative disorder of bilateral eyes (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410j',
                'Name': 'Anterior subcapsular polar cataract of bilateral eyes (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S15',
                'Name': 'Clouded, blurred or dim vision'
            },
            {
                'Id': 'S16',
                'Name': 'Need for brighter light for reading and other activities'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D10',
                'Name': 'Vision test'
            }
        ],
        'Treatment': [
            {
                'Id': 'T16',
                'Name': 'surgery'
            }
        ]
    },
    'Anaemia': {
        'Id': 'A10',
        'Parent': [
            {
                'Id': '212112410g',
                'Name': 'Disorder of cellular component of blood (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410g',
                'Name': 'Acquired Heinz body anemia (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S17',
                'Name': 'Shortness of breath'
            },
            {
                'Id': 'S18',
                'Name': 'Irregular heartbeat'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D11',
                'Name': 'Complete blood count, also called CBC'
            }
        ],
        'Treatment': [
            {
                'Id': 'T17',
                'Name': 'Iron deficiency anemia'
            },
            {
                'Id': 'T18',
                'Name': 'Anemia of chronic disease'
            }
        ]
    },
    'Depression': {
        'Id': 'A11',
        'Parent': [
            {
                'Id': '212112410h',
                'Name': 'Mood disorder (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410h',
                'Name': 'Acute depression (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S19',
                'Name': 'Feelings of sadness, tearfulness, emptiness or hopelessness'
            },
            {
                'Id': 'S20',
                'Name': 'Angry outbursts, irritability or frustration, even over small matters'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D12',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': 'T19',
                'Name': 'Anxious distress'
            },
            {
                'Id': 'T20',
                'Name': 'Melancholic features'
            }
        ]
    },
    'Glaucoma': {
        'Id': 'A12',
        'Parent': [
            {
                'Id': '212112410i',
                'Name': 'Disorder of eye proper (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410i',
                'Name': 'Absolute glaucoma (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S21',
                'Name': 'In later stages, difficulty seeing things in your central vision'
            },
            {
                'Id': 'S22',
                'Name': 'Gradually, patchy blind spots in your side vision. Side vision also is called peripheral vision'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D13',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': 'T21',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': 'T22',
                'Name': 'Checking for areas of vision loss, also known as a visual field test'
            }
        ]
    },
    'Gout': {
        'Id': 'A13',
        'Parent': [
            {
                'Id': '212112410k',
                'Name': 'Inflammatory disorder (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410k',
                'Name': 'Chronic gout without tophus (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S23',
                'Name': 'Intense joint pain'
            },
            {
                'Id': 'S24',
                'Name': 'Irritation, swelling and redness'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D14',
                'Name': 'Joint fluid test'
            }
        ],
        'Treatment': [
            {
                'Id': 'T23',
                'Name': 'Medicine that helps lessen the swelling'
            },
            {
                'Id': 'T24',
                'Name': 'Medicine that prevent gout complications by lowering uric acid in the blood'
            }
        ]
    },
    'Acute sinusitis': {
        'Id': 'A14',
        'Parent': [
            {
                'Id': '212112410L',
                'Name': 'Acute inflammatory disease (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410L',
                'Name': 'Acute bacterial sinusitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S25',
                'Name': 'Ear pressure'
            },
            {
                'Id': 'S26',
                'Name': 'Aching in the teeth'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D15',
                'Name': 'Nasal endoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': 'T25',
                'Name': 'Saline nasal spray'
            },
            {
                'Id': 'T26',
                'Name': 'Nasal corticosteroids'
            }
        ]
    },
    'Gingivitis': {
        'Id': 'A15',
        'Parent': [
            {
                'Id': '212112410m',
                'Name': 'Gingival disease (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410m',
                'Name': 'Acute gingivitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S27',
                'Name': 'Swollen or puffy gums'
            },
            {
                'Id': 'S28',
                'Name': 'Bad breath'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D16',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': 'T27',
                'Name': 'Review of your dental and medical history'
            },
            {
                'Id': 'T28',
                'Name': 'Looking at your teeth, gums, mouth and tongue'
            }
        ]
    },
    'Haemorrhoids': {
        'Id': 'A16',
        'Parent': [
            {
                'Id': '212112410n',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410n',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S29',
                'Name': 'Painless bleeding'
            },
            {
                'Id': 'S30',
                'Name': 'Itching or irritation in the anal area'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D17',
                'Name': 'Digital exam'
            }
        ],
        'Treatment': [
            {
                'Id': 'T29',
                'Name': 'Eat high-fiber foods'
            },
            {
                'Id': 'T30',
                'Name': 'Use topical treatments'
            }
        ]
    },
    'Constipation': {
        'Id': 'A17',
        'Parent': [
            {
                'Id': '212112410o',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410o',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S31',
                'Name': 'Fewer than three stools a week'
            },
            {
                'Id': 'S32',
                'Name': 'Hard, dry or lumpy stools'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D18',
                'Name': 'Look at the tissue of the anus and the surrounding skin'
            }
        ],
        'Treatment': [
            {
                'Id': 'T31',
                'Name': 'Eat a high-fiber diet'
            },
            {
                'Id': 'T32',
                'Name': 'Exercise most days of the week'
            }
        ]
    },
    'Diarrhea': {
        'Id': 'A18',
        'Parent': [
            {
                'Id': '212112410p',
                'Name': 'Disorder of anal canal (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410p',
                'Name': 'Bleeding hemorrhoids (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S33',
                'Name': 'Belly cramps or pain'
            },
            {
                'Id': 'S34',
                'Name': 'Vomiting'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D19',
                'Name': 'Flexible sigmoidoscopy or colonoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': 'T33',
                'Name': 'Antibiotics or anti-parasitics'
            }
        ]
    },
    'Gallstones': {
        'Id': 'A19',
        'Parent': [
            {
                'Id': '212112410q',
                'Name': 'Calculus in biliary tract (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410q',
                'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S35',
                'Name': 'Sudden and rapidly intensifying pain in the upper right portion of your abdomen'
            },
            {
                'Id': 'S36',
                'Name': 'Back pain between your shoulder blades'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D20',
                'Name': 'Abdominal ultrasound'
            }
        ],
        'Treatment': [
            {
                'Id': 'T34',
                'Name': 'Surgery to remove the gallbladder'
            },
            {
                'Id': 'T35',
                'Name': 'Medications to dissolve gallstones'
            }
        ]
    },
    'Endometriosis': {
        'Id': 'A20',
        'Parent': [
            {
                'Id': '212112410r',
                'Name': 'Calculus in biliary tract (disorder)'
            }
        ],
        'Children': [
            {
                'Id': '212112410r',
                'Name': 'Calculus of gallbladder with cholecystitis (disorder)'
            }
        ],
        'Symptoms': [
            {
                'Id': 'S37',
                'Name': 'Painful periods'
            },
            {
                'Id': 'S38',
                'Name': 'Pain with sex'
            }
        ],
        'Diagnosis': [
            {
                'Id': 'D21',
                'Name': 'Pelvic exam'
            }
        ],
        'Treatment': [
            {
                'Id': 'T36',
                'Name': 'Pain medicines'
            },
            {
                'Id': 'T37',
                'Name': 'Hormone therapy'
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
        # 'OperationalOntology': [],
        # 'PrivateOntology': ['Mark', 'Dr.Smith']
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
    client = MongoClient('localhost', 27017)  ## connect to the mongodb
    db = client['encryptedData']
    collection = db['data']



    ##-----------------------------------Topic obtain------------------------------------##  how many anchors are there
    hdbscanModel = HDBSCAN(   ##Clustering
        min_cluster_size=2,
        metric='euclidean',
        min_samples=1,
    )
    interestedStopWords = list(ENGLISH_STOP_WORDS.union(
        ['patient', 'doctor', 'yes', 'okay', 'right', 'brother', 'did', 'do', 'like', 'yeah', 'know', 'good', 'order'
            , 'thats', 'ago', 'wow', 'taking', 'think', 'long', 'oh', 'july', 'correct', 'day', 'im', 'didnt', 'having'
            , 'dont', 'dose', 'old', 'felt', 'amazing', 'dad', 'problem', 'today', 'let'
        , 'food', 'just', 'um', 'history', 'assistant', 'lifting'
         ]
    ))

    vectorizerModel = CountVectorizer(stop_words = interestedStopWords)   ##setting stop words
    topicModel = BERTopic(hdbscan_model = hdbscanModel, vectorizer_model = vectorizerModel)
    topic, probs = topicModel.fit_transform(list1)
    print(topic)
    print(max(topic))

    for i in range(max(topic) + 1):
        print(topicModel.get_topic(i))

    keywords = []
    keywordsNum = 0
    for i in range(max(topic) + 1):    ##take the first word in each topic as the topic representative
        keywords.append(topicModel.get_topic(i)[0][0])
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
        print(similarities, '\n')




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




    # ##------------------------------------Atom Assemble-------------------------------------##
    # Wrapper = {
    #        'Exclusive Rights Token': exclusiveToken,
    #        'Access Tokens': hashDiction,
    #        'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
    #        'Ontology Pointers': ontologyPointers
    #        }
    # Nucleus = {'encryptedData': cipherText}
    # atom1 = collection.insert_one({'Wrapper' : Wrapper, 'Nucleus' : Nucleus})
    #
    #
    #
    #
    # ##-----------------------------------leash ticket---------------------------------------##
    # leashTicket = {
    #     'leashedAtoms': {
    #         'Atom1': {
    #             'Id': '6a9682277fd3567fc334ad7e',
    #             'Type': 'DataAtom',
    #         }
    #     }
    # }
    # collection.insert_one(leashTicket)