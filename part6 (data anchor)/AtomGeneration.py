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
import requests
import csv

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
        'DomainOntology': DomainOntology,
        'OperationalOntology': [],
        'PrivateOntology': ['Mark', 'Dr.Smith']
    }


    ccc['context'] = context
    ccc['agents'] = involvedAgents
    ccc['ontology'] = ontology
    return ccc


##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntology = {
    'Asthma': {
        'Id': '11A',
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
                'Id': '29865431314A',
                'Name': 'Shortness of breath'
            },
            {
                'Id': '29865431315A',
                'Name': 'Chest tightness'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431316A',
                'Name': 'Methacholine challenge'
            },
            {
                'Id': '29865431317A',
                'Name': 'Imaging tests'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431318A',
                'Name': 'Inhaled corticosteroids'
            },
            {
                'Id': '29865431319A',
                'Name': 'Leukotriene modifiers'
            }
        ]
    },
    'AnalWarts': {
        'Id': '2212112B',
        'Parent': [
            {
                'Id': '212112410B',
                'Name': 'Anal Infection'
            }
        ],
        'Children': [],
        'Symptoms': [
            {
                'Id': '29865431311B',
                'Name': 'Bleeding with sex'
            },
            {
                'Id': '29865431312B',
                'Name': 'A cauliflower-like shape caused by a few warts close together'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313B',
                'Name': 'Pap tests'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314B',
                'Name': 'Imiquimod'
            },
            {
                'Id': '29865431315B',
                'Name': 'Trichloroacetic acid'
            }
        ]
    },
    'Heart block': {
        'Id': '2212112a',
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
                'Id': '29865431313a',
                'Name': 'fainting (syncope)'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313',
                'Name': 'Electrocardiogram (ECG or EKG)'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314',
                'Name': 'medications to reduce high blood pressure or reduce symptoms of heart failure'
            }
        ]
    },
    'Pneumonia': {
        'Id': '2212112b',
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
                'Id': '29865431311b',
                'Name': 'Chest pain when you breathe or cough'
            },
            {
                'Id': '29865431312b',
                'Name': 'Fever, sweating and shaking chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313b',
                'Name': 'Blood tests'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314b',
                'Name': 'Antibiotics'
            },
            {
                'Id': '29865431315b',
                'Name': 'Cough medicine'
            }
        ]
    },
    'Bronchitis': {
        'Id': '2212112c',
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
                'Id': '29865431311c',
                'Name': 'Sore throat'
            },
            {
                'Id': '29865431312c',
                'Name': 'Slight fever and chills'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313c',
                'Name': 'Chest X-ray'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314c',
                'Name': 'Cough medicine'
            },
            {
                'Id': '29865431315c',
                'Name': 'Antibiotics'
            }
        ]
    },
    'Tuberculosis': {
        'Id': '2212112d',
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
                'Id': '29865431311d',
                'Name': 'Low fever'
            },
            {
                'Id': '29865431312d',
                'Name': 'Tiredness'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313d',
                'Name': 'Listening to breathe with a stethoscope'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314d',
                'Name': 'Isoniazid'
            },
            {
                'Id': '29865431315d',
                'Name': 'Rifampin'
            }
        ]
    },
    'Gastritis': {
        'Id': '2212112',
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
                'Id': '29865431311e',
                'Name': 'Vomiting'
            },
            {
                'Id': '29865431312e',
                'Name': 'Nausea'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313e',
                'Name': 'Tests for H. pylori'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314e',
                'Name': 'Antibiotics to kill H. pylori'
            },
            {
                'Id': '29865431315e',
                'Name': 'Medicines that block acid production and promote healing'
            }
        ]
    },
    'Hepatitis A': {
        'Id': '2212112f',
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
                'Id': '29865431311f',
                'Name': 'Unusual tiredness and weakness'
            },
            {
                'Id': '29865431312f',
                'Name': 'Sudden nausea and vomiting and diarrhea'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313f',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314f',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': '29865431315f',
                'Name': 'Avoid alcohol and use medications with care'
            }
        ]
    },
    'Cataracts': {
        'Id': '2212112j',
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
                'Id': '29865431311j',
                'Name': 'Clouded, blurred or dim vision'
            },
            {
                'Id': '29865431312j',
                'Name': 'Need for brighter light for reading and other activities'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313j',
                'Name': 'Vision test'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314j',
                'Name': 'surgery'
            }
        ]
    },
    'Anaemia': {
        'Id': '2212112g',
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
                'Id': '29865431311g',
                'Name': 'Shortness of breath'
            },
            {
                'Id': '29865431312g',
                'Name': 'Irregular heartbeat'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313g',
                'Name': 'Complete blood count, also called CBC'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314g',
                'Name': 'Iron deficiency anemia'
            },
            {
                'Id': '29865431315g',
                'Name': 'Anemia of chronic disease'
            }
        ]
    },
    'Depression': {
        'Id': '2212112h',
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
                'Id': '29865431311h',
                'Name': 'Feelings of sadness, tearfulness, emptiness or hopelessness'
            },
            {
                'Id': '29865431312h',
                'Name': 'Angry outbursts, irritability or frustration, even over small matters'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313h',
                'Name': 'Blood tests are used to look for signs of the hepatitis A virus'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314h',
                'Name': 'Anxious distress'
            },
            {
                'Id': '29865431315h',
                'Name': 'Melancholic features'
            }
        ]
    },
    'Glaucoma': {
        'Id': '2212112i',
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
                'Id': '29865431311i',
                'Name': 'In later stages, difficulty seeing things in your central vision'
            },
            {
                'Id': '29865431312i',
                'Name': 'Gradually, patchy blind spots in your side vision. Side vision also is called peripheral vision'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313i',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314i',
                'Name': 'Get adequate food and liquid'
            },
            {
                'Id': '29865431315i',
                'Name': 'Checking for areas of vision loss, also known as a visual field test'
            }
        ]
    },
    'Gout': {
        'Id': '2212112k',
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
                'Id': '29865431311k',
                'Name': 'Intense joint pain'
            },
            {
                'Id': '29865431312k',
                'Name': 'Irritation, swelling and redness'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313k',
                'Name': 'Joint fluid test'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314k',
                'Name': 'Medicine that helps lessen the swelling'
            },
            {
                'Id': '29865431315k',
                'Name': 'Medicine that prevent gout complications by lowering uric acid in the blood'
            }
        ]
    },
    'Acute sinusitis': {
        'Id': '2212112L',
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
                'Id': '29865431311L',
                'Name': 'Ear pressure'
            },
            {
                'Id': '29865431312L',
                'Name': 'Aching in the teeth'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313L',
                'Name': 'Nasal endoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314L',
                'Name': 'Saline nasal spray'
            },
            {
                'Id': '29865431315L',
                'Name': 'Nasal corticosteroids'
            }
        ]
    },
    'Gingivitis': {
        'Id': '2212112m',
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
                'Id': '29865431311m',
                'Name': 'Swollen or puffy gums'
            },
            {
                'Id': '29865431312m',
                'Name': 'Bad breath'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313m',
                'Name': 'Measuring intraocular pressure, also called tonometry'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314m',
                'Name': 'Review of your dental and medical history'
            },
            {
                'Id': '29865431315m',
                'Name': 'Looking at your teeth, gums, mouth and tongue'
            }
        ]
    },
    'Haemorrhoids': {
        'Id': '2212112n',
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
                'Id': '29865431311n',
                'Name': 'Painless bleeding'
            },
            {
                'Id': '29865431312n',
                'Name': 'Itching or irritation in the anal area'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313n',
                'Name': 'Digital exam'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314n',
                'Name': 'Eat high-fiber foods'
            },
            {
                'Id': '29865431315n',
                'Name': 'Use topical treatments'
            }
        ]
    },
    'Constipation': {
        'Id': '2212112o',
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
                'Id': '29865431311o',
                'Name': 'Fewer than three stools a week'
            },
            {
                'Id': '29865431312o',
                'Name': 'Hard, dry or lumpy stools'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313o',
                'Name': 'Look at the tissue of the anus and the surrounding skin'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314o',
                'Name': 'Eat a high-fiber diet'
            },
            {
                'Id': '29865431315o',
                'Name': 'Exercise most days of the week'
            }
        ]
    },
    'Diarrhea': {
        'Id': '2212112p',
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
                'Id': '29865431311p',
                'Name': 'Belly cramps or pain'
            },
            {
                'Id': '29865431312p',
                'Name': 'Vomiting'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313p',
                'Name': 'Flexible sigmoidoscopy or colonoscopy'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314p',
                'Name': 'Antibiotics or anti-parasitics'
            }
        ]
    },
    'Gallstones': {
        'Id': '2212112q',
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
                'Id': '29865431311q',
                'Name': 'Sudden and rapidly intensifying pain in the upper right portion of your abdomen'
            },
            {
                'Id': '29865431312q',
                'Name': 'Back pain between your shoulder blades'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313q',
                'Name': 'Abdominal ultrasound'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314q',
                'Name': 'Surgery to remove the gallbladder'
            },
            {
                'Id': '29865431315q',
                'Name': 'Medications to dissolve gallstones'
            }
        ]
    },
    'Endometriosis': {
        'Id': '2212112r',
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
                'Id': '29865431311r',
                'Name': 'Painful periods'
            },
            {
                'Id': '29865431312r',
                'Name': 'Pain with sex'
            }
        ],
        'Diagnosis': [
            {
                'Id': '29865431313r',
                'Name': 'Pelvic exam'
            }
        ],
        'Treatment': [
            {
                'Id': '29865431314r',
                'Name': 'Pain medicines'
            },
            {
                'Id': '29865431315r',
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

if __name__ == '__main__':
    csvFile = open('data/data.csv', 'r', encoding = 'utf-8')
    readLines = csv.reader(csvFile)

    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']

    ##------------------------------------------data obtaining------------------------------------##
    line = 1
    list1 = []  ## prepare for topics extraction
    data = ''  ## the data to be encrypted
    for row in readLines:
        data += row[3]
        list1.append(row[3])

        line += 1


        if line % 20 == 0:    ##20 dialogues have been read into memory, now assemble an atom
            ##-----------------------------------------conception context obtaining---------------------------------##
            ccc = conceptionContextGenerator()
            print('this is the conception context: ', ccc)
            ontologyPointers = []

            print(list1, data)

            ##-----------------------------------keywords obtain------------------------------------##  how many anchors are there
            hdbscanModel = HDBSCAN(
                min_cluster_size=2, min_samples=1
            )

            interestedStopWords = list(text.ENGLISH_STOP_WORDS.union(
                {'patient', 'doctor', 'yes', 'okay', 'right', 'brother', 'did', 'do', 'does', 'like', 'yeah', 'know',
                 'good', 'order', 'thats', 'ago', 'wow', 'taking'
                    , 'think', 'long', 'oh', 'july', 'correct', 'day', 'im', 'didnt', 'having', 'dont', 'dose', 'old',
                 'felt', 'amazing', 'dad', 'problem', 'today', 'let'
                    , 'food', 'just'
                 }
            ))

            vectorizerModel = CountVectorizer(stop_words=interestedStopWords)  ##setting stop words

            topicModel = BERTopic(hdbscan_model=hdbscanModel, vectorizer_model=vectorizerModel)

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
            symmetricKey = Fernet.generate_key()  ##generate a random symmetric key
            print("This is the symmetric key:", symmetricKey)
            fernet = Fernet(symmetricKey)
            cipherText = fernet.encrypt(dataBytes)  ##Encrypt the sensitive data
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
                    if (j[0] != 'Id') and (j[0] != 'Parent') and (j[0] != 'Children'):
                        for k in j[1]:
                            sen.append(k['Name'])
                            nodesNum += 1

                print(sen)

                print('those are the sentences:', sen, '\n')
                embedding = model.encode(sen)
                similarities = model.similarity(embedding, embedding)
                print('let us look at the similarity result: ', similarities, '\n')

                ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
                posi = (0, 0)  ##find the most relevant Domain Ontology with for loop
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


            ##------------------------------------Atom Assemble-------------------------------------##
            Wrapper = {
                'Exclusive Rights Token': exclusiveToken,
                'Access Tokens': hashDiction,
                'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
                'Ontology Pointers': ontologyPointers
            }
            Nucleus = {'encryptedData': cipherText}
            atom1 = collection.insert_one({'Wrapper': Wrapper, 'Nucleus': Nucleus})

        else:
            continue














#
#
#

#
#
#
#
#     ##-----------------------------------leash ticket---------------------------------------##
#     leashTicket = {
#         'leashedAtoms': {
#             'Atom1': {
#                 'Id': str(atom1.inserted_id),
#                 'Type': 'DataAtom',
#             },
#             'Atom2': {
#                 'Id': '6a421a637137da02587894cd',
#                 'Type': 'DataAtom',
#             }
#         }
#     }
#     collection.insert_one(leashTicket)