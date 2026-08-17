from keybert import KeyBERT
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import hashlib
from sentence_transformers import SentenceTransformer

##-----------------------------------------Ontology Selection----------------------------------------------##
DomainOntologyList = {'DomainOnto1': 'Transmission', 'DomainOnto2': 'Propagation',
                      'DomainOnto3': 'Diagnosis', 'DomainOnto4': 'Symptoms',
                      'DomainOnto5': 'BiologicalRiskLevel', 'DomainOnto6': 'Detection',
                      'DomainOnto7': 'Virus', 'DomainOnto8': 'Bacteria',
                      'DomainOnto9': 'Diagnosis', 'DomainOnto10': 'Prevention',
                      'DomainOnto11': 'Control', 'DomainOnto12': 'Treatment'}
OperationalOntologyList = {'OperOnto1': 'Agricultural_activities', 'OperOnto2': 'Forest_Wildlife',
                           'OperOnto3': 'PoorVentilation_Area', 'OperOnto4': 'Rats_Habitation',
                           'OperOnto5': 'Rats_Elimination', 'OperOnto6': 'Rats_BiologicalControl'}
AuthoritativeOntologyList = {'AuthOnto1': 'WorldHealthOrganization', 'AuthOnto2': 'RoyalHospital',
                             'AuthOnto3': 'US_Government', 'AuthOnto4': 'Bureau_of_Meteorology'}
## private_1 ---->  WHO,  private_2 -------> RoyalHospital, private_3 -----> US_Government
PrivateOntologyList = {'PrivateOnto1': 'Research_Use_Only', 'PrivateOnto2': 'Commercial_Use_Allowed', 'PrivateOnto3': 'Secret_Data', 'PrivateOnto4': 'Public_Broadcast'}

ontologyPointers = ['PrivateOnto4']
ontologyPointers3 = ['PrivateOnto4']
ontologyPointers2 = ['PrivateOnto4']


if __name__ == '__main__':
    ##------------------------------------------data obtaining------------------------------------##
    with open("article.txt", "r", encoding='utf-8') as file:
        data = file.read()
    print("This is data:", data)


    with open("article2.txt", "r", encoding='utf-8') as file2:
        data2 = file2.read()
    print("This is data:", data2)


    with open("article3.txt", "r", encoding='utf-8') as file3:
        data3 = file3.read()
    print("This is data:", data3)



    ##-----------------------------database activation---------------------------##
    client = MongoClient('localhost', 27017)  ## save the encrypted text into database
    db = client['encryptedData']
    collection = db['data']


    ##-----------------------------------keywords obtain------------------------------------##  how many anchors are there
    wordCount = len(data.split()) ##calculating how many words are there in the data
    keywordsNum = int(wordCount * 0.05)
    wordCount2 = len(data2.split())  ##calculating how many words are there in the data
    keywordsNum2 = int(wordCount2 * 0.05)
    wordCount3 = len(data3.split())  ##calculating how many words are there in the data
    keywordsNum3 = int(wordCount3 * 0.05)
    # print("The number of keywords", int(wordCount * 0.05))
    keybertModel = KeyBERT()
    print("we are processing keyword extraction")
    keywords = keybertModel.extract_keywords(
        data,
        stop_words = 'english',
        top_n = max(3, keywordsNum),  ##for the data with fewer words, at least 3 keywords should be identified
        use_mmr = True  ## exclude those similar words, such as apple and apples
    )

    keywords2 = keybertModel.extract_keywords(
        data2,
        stop_words='english',
        top_n=max(3, keywordsNum2),  ##for the data with fewer words, at least 3 keywords should be identified
        use_mmr=True  ## exclude those similar words, such as apple and apples
    )

    keywords3 = keybertModel.extract_keywords(
        data3,
        stop_words='english',
        top_n=max(3, keywordsNum3),  ##for the data with fewer words, at least 3 keywords should be identified
        use_mmr=True  ## exclude those similar words, such as apple and apples
    )
    # print(keywords)



    ##-----------------------------------------symmetric encryption----------------------------------------##
    dataBytes = data.encode()
    symmetricKey = Fernet.generate_key()       ##generate a random symmetric key
    print("This is the symmetric key:", symmetricKey)
    fernet = Fernet(symmetricKey)
    cipherText = fernet.encrypt(dataBytes)       ##Encrypt the sensitive data
    print('\nThis is the encrypted data:', cipherText)



    dataBytes2 = data2.encode()
    symmetricKey2 = Fernet.generate_key()  ##generate a random symmetric key
    print("This is the symmetric key2:", symmetricKey2)
    fernet = Fernet(symmetricKey2)
    cipherText2 = fernet.encrypt(dataBytes2)  ##Encrypt the sensitive data
    print('\nThis is the encrypted data:', cipherText2)



    dataBytes3 = data3.encode()
    symmetricKey3 = Fernet.generate_key()  ##generate a random symmetric key
    print("This is the symmetric key3:", symmetricKey3)
    fernet = Fernet(symmetricKey3)
    cipherText3 = fernet.encrypt(dataBytes3)  ##Encrypt the sensitive data
    print('\nThis is the encrypted data:', cipherText3)



    ##-------------------------------------data signing and sealing (exclusive rights token & access token)-----------------------------------##
    exclusiveToken = ''    ##Only the WHO has the exclusive right.
    exclusiveToken2 = ''  ##Only the WHO has the exclusive right.
    exclusiveToken3 = ''  ##Only the WHO has the exclusive right.
    hashDiction = {}       ##Agents token dictionary
    hashDiction2 = {}  ##Agents token dictionary
    hashDiction3 = {}  ##Agents token dictionary
    for i in range(1, 4):
        with open("../asymKeys/public_{0}.pem".format(i), 'rb') as f:  ##obtain the saved public key
            publicKey = serialization.load_pem_public_key(f.read())
        encryptedSymKey = publicKey.encrypt(
            symmetricKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )


        encryptedSymKey2 = publicKey.encrypt(
            symmetricKey2,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )


        encryptedSymKey3 = publicKey.encrypt(
            symmetricKey3,
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


        publicKeyBytes2 = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey2 = hashlib.sha256(publicKeyBytes2).hexdigest()
        hashDiction[hashedPublicKey2] = encryptedSymKey2


        publicKeyBytes3 = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        hashedPublicKey3 = hashlib.sha256(publicKeyBytes3).hexdigest()
        hashDiction[hashedPublicKey3] = encryptedSymKey3


        if i == 1:
            exclusiveToken = hashedPublicKey  ##exclusive token generation
            exclusiveToken2 = hashedPublicKey2  ##exclusive token generation
            exclusiveToken3 = hashedPublicKey3  ##exclusive token generation
        # print('\nThis is the encrypted symmetric key:', encryptedSymKey




    ##------------------------------------Ontology Latching--------------------------------------##
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = []
    for i in range(len(keywords)):
        sentences.append(keywords[i][0])

    i = 1
    while 'DomainOnto{0}'.format(i) in DomainOntologyList:          ##Including all other Domain Ontologies
        sentences.append(DomainOntologyList['DomainOnto{0}'.format(i)])
        i += 1
    print('those are the sentences:', sentences, '\n')
    embedding = model.encode(sentences)
    similarities = model.similarity(embedding, embedding)
    print('let us look at the similarity result: ', similarities, '\n')



    sentences2 = []
    for i in range(len(keywords2)):
        sentences2.append(keywords2[i][0])

    i = 1
    while 'DomainOnto{0}'.format(i) in DomainOntologyList:  ##Including all other Domain Ontologies
        sentences2.append(DomainOntologyList['DomainOnto{0}'.format(i)])
        i += 1
    print('those are the sentences:', sentences2, '\n')
    embedding2 = model.encode(sentences2)
    similarities2 = model.similarity(embedding2, embedding2)
    print('let us look at the similarity result: ', similarities2, '\n')




    sentences3 = []
    for i in range(len(keywords3)):
        sentences3.append(keywords3[i][0])

    i = 1
    while 'DomainOnto{0}'.format(i) in DomainOntologyList:  ##Including all other Domain Ontologies
        sentences3.append(DomainOntologyList['DomainOnto{0}'.format(i)])
        i += 1
    print('those are the sentences:', sentences3, '\n')
    embedding3 = model.encode(sentences3)
    similarities3 = model.similarity(embedding3, embedding3)
    print('let us look at the similarity result: ', similarities3, '\n')


    ##---------------------------------locating the ontology with the highest relevance-------------------------------------------##
    posi = (0, 0)    ##find the most relevant Domain Ontology with for loop
    value = 0
    for i in range(0, keywordsNum):
        for j in range(keywordsNum, keywordsNum + len(DomainOntologyList)):
            if similarities[i][j] > value:
                value = similarities[i][j]
                posi = [i, j]
    print(posi)
    print(similarities[posi[0]][posi[1]])
    most_relevant_DomainOnto = 'DomainOnto{0}'.format(posi[1] - keywordsNum + 1)
    # print(most_relevant_DomainOnto)
    ontologyPointers.append(most_relevant_DomainOnto)    ##put the most relevant one into the ontology pointer list


    posi = (0, 0)  ##find the most relevant Domain Ontology with for loop
    value = 0
    for i in range(0, keywordsNum2):
        for j in range(keywordsNum2, keywordsNum2 + len(DomainOntologyList)):
            if similarities2[i][j] > value:
                value = similarities2[i][j]
                posi = [i, j]
    print(posi)
    print(similarities2[posi[0]][posi[1]])
    most_relevant_DomainOnto = 'DomainOnto{0}'.format(posi[1] - keywordsNum2 + 1)
    # print(most_relevant_DomainOnto)
    ontologyPointers2.append(most_relevant_DomainOnto)  ##put the most relevant one into the ontology pointer list


    posi = (0, 0)  ##find the most relevant Domain Ontology with for loop
    value = 0
    for i in range(0, keywordsNum3):
        for j in range(keywordsNum3, keywordsNum3 + len(DomainOntologyList)):
            if similarities3[i][j] > value:
                value = similarities3[i][j]
                posi = [i, j]
    print(posi)
    print(similarities3[posi[0]][posi[1]])
    most_relevant_DomainOnto = 'DomainOnto{0}'.format(posi[1] - keywordsNum3 + 1)
    # print(most_relevant_DomainOnto)
    ontologyPointers3.append(most_relevant_DomainOnto)  ##put the most relevant one into the ontology pointer list



    ##------------------------------------Atom Assemble-------------------------------------##
    Wrapper = {
           'Exclusive Rights Token': exclusiveToken,
           'Access Tokens': hashDiction,
           'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
           'Ontology Pointers': ontologyPointers
           }
    Nucleus = {'encryptedData': cipherText}
    atom1 = collection.insert_one({'Wrapper' : Wrapper, 'Nucleus' : Nucleus})


    Wrapper = {
        'Exclusive Rights Token': exclusiveToken2,
        'Access Tokens': hashDiction2,
        'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
        'Ontology Pointers': ontologyPointers2
    }
    Nucleus = {'encryptedData': cipherText2}
    atom2 = collection.insert_one({'Wrapper': Wrapper, 'Nucleus': Nucleus})



    Wrapper = {
        'Exclusive Rights Token': exclusiveToken3,
        'Access Tokens': hashDiction3,
        'Authority Pointer': ['AuthOnto1', 'AuthOnto2', 'AuthOnto3'],
        'Ontology Pointers': ontologyPointers3
    }
    Nucleus = {'encryptedData': cipherText3}
    atom3 = collection.insert_one({'Wrapper': Wrapper, 'Nucleus': Nucleus})



    ##-----------------------------------leash ticket---------------------------------------##
    leashTicket = {
        'leashedAtoms': {
            'Atom1': {
                'Id': str(atom1.inserted_id),
                'Type': 'DataAtom',
            },
            'Atom2': {
                'Id': str(atom2.inserted_id),
                'Type': 'DataAtom',
            },
            'Atom3': {
                'Id': str(atom3.inserted_id),
                'Type': 'DataAtom',
            }
        }
    }
    collection.insert_one(leashTicket)