from typing import Optional
import opendht as dht
import hashlib
import msgpack
import argparse
import requests
from typing import NamedTuple
import subprocess

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
    "friends": [
        hashlib.md5("stefanbroecker@ucdavis.edu".encode('utf-8')).hexdigest(),
        hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest()
    ]
}
# print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(unique_key), dht.Value(packed_dict))

# Stefan
uunique_key = hashlib.md5("stefanbroecker@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
    "name": "Stefan",
    "packages": [
        "rich",
        "jsonrpc",
        "matplotlib"
    ],
    "friends": [
        hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest(),
        hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest(),
        hashlib.md5("wu@ucdavis.edu".encode('utf-8')).hexdigest()
    ]
}
# print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(uunique_key), dht.Value(packed_dict))

# David
uunique_key = hashlib.md5("david@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
    "name": "David",
    "packages": [
        "plotly",
        "requests",
        "matplotlib"
    ],
    "friends": [ 
        hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest() 
    ]
}
# print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(uunique_key), dht.Value(packed_dict))

# Dr. Wu
wunique_key = hashlib.md5("wu@ucdavis.edu".encode('utf-8')).hexdigest()
data_dict  = {
    "name": "Felix Wu",
    "packages": [
        "plotly",
        "requests",
        "matplotlib"
    ],
    "friends": [ 
        hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest() 
    ]
}
# print("Putting dict on DHT: ", data_dict)
packed_dict = msgpack.packb(data_dict)
node.put(dht.InfoHash.get(wunique_key), dht.Value(packed_dict))

# Retrieve
results = node.get(dht.InfoHash.get(unique_key))
for r in results:
    first = msgpack.unpackb(r.data)
    print("Found entry: ", first)
    print("Searching for friends")
    friends = first["friends"]
    for f in friends:
        result = node.get(dht.InfoHash.get(f))[-1]
        friend_dict = msgpack.unpackb(result.data)
        print(friend_dict)


def find_friends(root: str, state: list, depth: int, target_depth: int, friends_visited: set) -> dict:
    state = []
    friends_visited.add(root)
    results = node.get(dht.InfoHash.get(root))
    if results:
        to_check = []
        r = msgpack.unpackb(results[-1].data)
        friends = r["friends"]
        for friend in friends:
            if not friend in friends_visited:
                friends_visited.add(friend)
                to_check.append(friend)
                inner_results = node.get(dht.InfoHash.get(friend))
                if results:
                    inner_r = msgpack.unpackb(inner_results[-1].data)
                    inner_r["depth"] = depth
                    state.append(inner_r)
        if depth < target_depth:
            for friend in to_check:
                state.extend(find_friends(friend, state, depth + 1, target_depth, friends_visited))
    return state

def updateDHT(package: str, owner: str):
    result = node.get(dht.InfoHash.get(owner))
    if result:
        unpacked = msgpack.unpackb(result[-1].data)
        unpacked["packages"].append(package)
        packed_dict = msgpack.packb(unpacked)
        node.put(dht.InfoHash.get(owner), dht.Value(packed_dict))


def fetch_pypi(package: str) -> Optional[str]:
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    response.raise_for_status()
    # access JSOn content
    # print(response.json()['info'])
    json_response = response.json()
    project_urls =  json_response['info']['project_urls']
    # print(json_response['info']['project_urls'])
    return project_urls.get('Github', project_urls.get('Source', project_urls.get('Source Code', project_urls.get('Homepage', 'NOT_FOUND'))))

github_cache = {}
def fetch_github(owner: str, project: str) -> tuple[int, int]:
    if (owner, project) not in github_cache:
        response = requests.get(f"https://api.github.com/repos/{owner}/{project}")
        response.raise_for_status()
        # access JSOn content
        json_response = response.json()
        github_cache[(owner, project)] = json_response['stargazers_count'], json_response['forks_count']
    return github_cache[(owner, project)]

def generateScore(package: str, owner: str):
    friends = find_friends(owner, [], 1, 2, set())
    d = 1000
    ct = 0.0
    for f in friends:
        if package in f["packages"]:
            ct += 1/f["depth"]
            d = min(f["depth"], d)
    package_git = fetch_pypi(package).split('/')
    stars, forks = fetch_github(package_git[-2], package_git[-1])
    if ct > 0.0:
        return ((ct * 1/d), (forks * stars))
    else:
        return (0, (forks * stars))


# https://pypi.org/pypi/sampleproject/json

social_scores = {'numpy': 89/100}
# print(friends)

# for friend in friends:
#     for package in friend['packages']:
#         package_git = fetch_pypi(package).split('/')
#         stars, forks = fetch_github(package_git[-2], package_git[-1])
#         social_scores[package] = friend['depth'] * forks * stars

parser = argparse.ArgumentParser()
parser.add_argument('args', nargs='+')
args = parser.parse_args().args
if args[0] == 'pip':
    if len(args) > 2 and args[1] == 'install':
        package = args[2]
        social_score, github_score = generateScore(package, wunique_key)
        question = lambda q: input(q).lower().strip()[0] == "y"
        if question(f"The package '{args[2]}' has a social score of {social_score} and a github score of {github_score}. Are you sure you want to proceed? "):
            print("Installing package:")
            # subprocess.run(list(args))
            updateDHT(package, wunique_key)
        else:
            print("Installation aborted")
elif args[0] in ('npm', 'yarn'):
    print("NPM support is next")
else:
    print("This package manager is not supported yet. Sorry.")

results = node.get(dht.InfoHash.get(wunique_key))
print(msgpack.unpackb(results[-1].data))

# TODO:
"""
- It needs a name: spm (social package manager) ?
- The packages are hard coded. When a user runs spm install x, it should add x to their hash table entry
- The calculation sucks and isn't correct, it needs to weight the amount of friends and friends of friends.
- Github stats should weigh less
- the ui could be improved
- we need a demo that shows how it works across several machines
"""