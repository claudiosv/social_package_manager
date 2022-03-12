from typing import Optional
import opendht as dht
import hashlib
import msgpack
import argparse
import requests
from typing import NamedTuple

node = dht.DhtRunner()
node.run()

# Join the network through any running node,
# here using a known bootstrap node.
node.bootstrap("bootstrap", "4222")
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

# Stefan
uunique_key = hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
        "name": "David",
    "packages": [
        "plotly",
        "requests",
        "matplotlib"
    ],
    "friends": [ hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest() ]
}
print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(uunique_key), dht.Value(packed_dict))





# Retrieve
# results = node.get(dht.InfoHash.get(unique_key))[0]
# #for r in results:
# first = msgpack.unpackb(results.data)
# print("Found entry: ", first)
# print("Searching for friends")
friends_visited = set()

def find_friends(friends: list, state: dict, depth: int, friends_visited: set) -> dict:
    state = {}
    for friend in friends:
        if not friend in friends_visited:
            friends_visited.add(friend)
            results = node.get(dht.InfoHash.get(friend))
            if results:
                first = msgpack.unpackb(results[0].data)
                first['depth'] = depth
                print("Found friend:", first)
                state |= first
                state |= find_friends(first['friends'], state, depth+1, friends_visited)
    return state

def fetch_pypi(package: str) -> Optional[str]:
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    response.raise_for_status()
    # access JSOn content
    print(response.json()['info'])
    return response.json()['info']['project_urls']['Github']
def fetch_github(owner: str, project: str) -> tuple[int, int]:
    response = requests.get(f"https://api.github.com/repos/{owner}/{project}")
    response.raise_for_status()
    # access JSOn content
    json = response.json()
    return json['stargazers_count'], json['forks_count']

friends = find_friends([unique_key], dict(), 0, friends_visited)
print(friends)
# https://pypi.org/pypi/sampleproject/json
social_scores = {'numpy': 89/100}
for friend in friends:
    for package in friends['packages']:
        package_git = fetch_pypi(package).split('/')
        stars, forks = fetch_github(package_git[-2], package_git[-1])
        social_scores[package] = friend['depth'] * forks * stars



