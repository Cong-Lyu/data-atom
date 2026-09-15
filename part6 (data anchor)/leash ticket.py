from pymongo import MongoClient


client = MongoClient('localhost', 27017)  ## connect to the mongodb
db = client['encryptedData']
collection = db['data']

##-----------------------------------leash ticket---------------------------------------##
leashTicket = {
    'leashedAtoms': {
        'Atom1': {
            'Id': '6a9682277fd3567fc334ad7e',
            'Type': 'DataAtom',
        }
    }
}
collection.insert_one(leashTicket)