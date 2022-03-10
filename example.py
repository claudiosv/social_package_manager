import opendht as dht
import hashlib
import msgpack

node = dht.DhtRunner()
node.run()

# Join the network through any running node,
# here using a known bootstrap node.
node.bootstrap("bootstrap.jami.net", "4222")
unique_key = hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
    "name": "Claudio",
    "packages": [
        "numpy",
        "jsonrpc",
        "pandas"
    ],
    "friends": [ hashlib.md5("stefanbroeger@ucdavis.edu".encode('utf-8')).hexdigest(),
    hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest() ]
}
print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(unique_key), dht.Value(packed_dict))

# Stefan
uunique_key = hashlib.md5("stefanbroeger@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
        "name": "Stefan",
    "packages": [
        "rich",
        "jsonrpc",
        "matplotlib"
    ],
    "friends": [ hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest(),
    hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest() ]
}
print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(uunique_key), dht.Value(packed_dict))





# Retrieve
results = node.get(dht.InfoHash.get(unique_key))[0]
#for r in results:
first = msgpack.unpackb(results.data)
print("Found entry: ", first)
print("Searching for friends")
for friend in first['friends']:
    results = node.get(dht.InfoHash.get(friend))
    if results:
        first = msgpack.unpackb(results[0].data)
        print("Found friend:", first)

