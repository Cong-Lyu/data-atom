from keybert import KeyBERT
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import hashlib
from sentence_transformers import SentenceTransformer
import time


##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntologyList = {'DomainOnto1': 'symptoms', 'DomainOnto2': 'MedicalHistory',
                      'DomainOnto3': 'Diagnosis', 'DomainOnto4': 'Tests'}
OperationalOntologyList = {'OperOnto1': 'medicalConsultation', 'OperOnto2': 'InpatientAdmission'}
AuthoritativeOntologyList = {'AuthOnto1': 'Patient', 'AuthOnto2': 'RoyalHospital',
                             'AuthOnto3': 'Dr. Steve'}
## private_1 ---->  WHO,  private_2 -------> RoyalHospital, private_3 -----> US_Government
PrivateOntologyList = {'PrivateOnto1': 'patientAndDoctorsOnly'}


def conceptionContextGenerator():
    ccc = {}
    ##-----------------------------------context--------------------------------------##
    timeStamp = time.time()
    context = {
        'location' : 'America',
        'timeStamp' : timeStamp
    }


    ##----------------------------------agent ascertain---------------------------------##
    involvedAgents = []
    for i in range(1, 4):
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
        'PrivateOntology': 'PrivateOnto4'
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
    with open("data1.txt", "r", encoding='utf-8') as file:
        data = file.read()
    print("This is data:", data)


    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']



    ##-----------------------------------keywords obtain------------------------------------##  how many anchors are there
    wordCount = len(data.split()) ##calculating how many words are there in the data
    keywordsNum = int(wordCount * 0.05)
    print("The number of keywords", int(wordCount * 0.05))
    keybertModel = KeyBERT()
    print("we are processing keyword extraction")
    keywords = keybertModel.extract_keywords(
        data,
        stop_words = 'english',
        top_n = max(3, keywordsNum),  ##for the data with fewer words, at least 3 keywords should be identified
        use_mmr = True  ## exclude those similar words, such as apple and apples
    )
    print(keywords)



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
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i][0])

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
    # print(most_relevant_DomainOnto)
    ontologyPointers.append(most_relevant_DomainOnto)    ##put the most relevant one into the ontology pointer list




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
            }
        }
    }
    collection.insert_one(leashTicket)