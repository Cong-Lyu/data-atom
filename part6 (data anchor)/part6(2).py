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

##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntologyList = {'DomainOnto1': 'Duration', 'DomainOnto2': 'Enquiry',
                      'DomainOnto3': 'Diagnosis', 'DomainOnto4': 'Symptoms'
                      }
OperationalOntologyList = {'OperOnto1': 'medicalConsultation', 'OperOnto2': 'InpatientAdmission'}
AuthoritativeOntologyList = {'AuthOnto1': 'Patient', 'AuthOnto2': 'Hospital',
                             'AuthOnto3': 'Doctor'}
PrivateOntologyList = {'PrivateOnto1': 'patientAndDoctorsOnly'}

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
    for i in range(1, 5):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
        involvedAgents.append({
            'agentAuthorityPointer': 'AuthOnto{0}'.format(i),
            'publicKey': publicKey
        })


    ##-----------------------------------ontology base-------------------------------------##
    ontologyBase = {
        'DomainOntology': DomainOntologyList,
        'OperationalOntology': OperationalOntologyList,
        'PrivateOntology': 'PrivateOnto1'
    }


    ccc['context'] = context
    ccc['agents'] = involvedAgents
    ccc['ontologyBase'] = ontologyBase
    return ccc



if __name__ == '__main__':
    ##-----------------------------------------conception context obtaining---------------------------------##
    ccc = conceptionContextGenerator()
    print('this is the conception context: ', ccc)
    ontologyPointers = ['PrivateOnto4']


    ##------------------------------------------data obtaining------------------------------------##
    list1 = []   ## prepare for topics extraction
    data = ''   ## the data to be encrypted
    for i in range(20):
        with open("articles/article{0}.txt".format(i + 1), "r", encoding='utf-8') as file:
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
    for i in range(1, 5):
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
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i])

    i = 1
    while 'DomainOnto{0}'.format(i) in ccc['ontologyBase']['DomainOntology']:          ##Including all other Domain Ontologies
        sentences.append(ccc['ontologyBase']['DomainOntology']['DomainOnto{0}'.format(i)])
        i += 1
    print('those are the sentences:', sentences, '\n')
    embedding = model.encode(sentences)
    similarities = model.similarity(embedding, embedding)
    print('let us look at the similarity result: ', similarities, '\n')




    ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
    posi = (0, 0)    ##find the most relevant Domain Ontology with for loop
    value = 0
    for i in range(0, keywordsNum):
        for j in range(keywordsNum, keywordsNum + len(ccc['ontologyBase']['DomainOntology'])):
            if similarities[i][j] > value:
                value = similarities[i][j]
                posi = [i, j]
    print(posi)
    print(similarities[posi[0]][posi[1]])
    most_relevant_DomainOnto = 'DomainOnto{0}'.format(posi[1] - keywordsNum + 1)
    print(most_relevant_DomainOnto)
    ontologyPointers.append(most_relevant_DomainOnto)    ##put the most relevant one into the ontology pointer list




    ##------------------------------------Atom Assemble-------------------------------------##
    Wrapper = {
           'Exclusive Rights Token': exclusiveToken,
           'Access Tokens': hashDiction,
           'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3', 'AuthOnto4'],
           'Ontology Pointers': ontologyPointers
           }
    Nucleus = {'encryptedData': cipherText}
    atom1 = collection.insert_one({'Wrapper' : Wrapper, 'Nucleus' : Nucleus})




    # ##-----------------------------------leash ticket---------------------------------------##
    # leashTicket = {
    #     'leashedAtoms': {
    #         'Atom1': {
    #             'Id': str(atom1.inserted_id),
    #             'Type': 'DataAtom',
    #         }
    #     }
    # }
    # collection.insert_one(leashTicket)