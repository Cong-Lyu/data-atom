from datetime import timedelta
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.collection import UpsertOptions
from couchbase.transcoder import RawBinaryTranscoder
from couchbase.options import GetOptions

from pymongo import MongoClient
from bson import ObjectId
import pickle

##---------------------connect to MongoDB and obtain the atom by its ID--------------------------##
client = MongoClient('localhost', 27017)  ## save the encrypted text into database
db = client['encryptedData']
db2 = client['atomTransfer']
atomExample = db['data'].find_one({"_id": ObjectId('6a9682277fd3567fc334ad7e')})
print('atom from MongoDB: ', atomExample)
atom = pickle.dumps(atomExample)

##------------------------------connect to couchbase----------------------------##
username = 'Administrator'
password = '123456'
bucket = 'data_atom'

auth = PasswordAuthenticator(username, password)
cluster = Cluster.connect('couchbase://127.0.0.1', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
bucketDB = cluster.bucket(bucket)
collection = bucketDB.default_collection()
# result = collection.upsert("atom", atom, UpsertOptions(transcoder=RawBinaryTranscoder()))
# cas = result.cas

##-----------------------atom retrieval---------------------------##
atomRetrieved = collection.get(
    "atom",
    GetOptions(transcoder=RawBinaryTranscoder())
)
atomBytes = atomRetrieved.content_as[bytes]
atomObtained = pickle.loads(atomBytes)
print('atom from Couchbase: ', atomObtained)
print('are they the same atom?  ', atomObtained == atomExample)


