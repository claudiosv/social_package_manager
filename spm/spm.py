from typing import Optional
import opendht as dht
import hashlib
import msgpack
import argparse
import requests
from typing import NamedTuple
import subprocess
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.tree import Tree
console = Console()

node = dht.DhtRunner()
node.run()
wunique_key = hashlib.md5("wu@ucdavis.edu".encode('utf-8')).hexdigest()
my_unique_key = hashlib.md5("cvspiess@ucdavis.edu".encode('utf-8')).hexdigest()

# Join the network through any running node,
# here using a known bootstrap node.
def bootstrap():
    node.bootstrap("bootstrap.jami.net", "4222")
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
    console.print(":sparkles:", "Putting dict on DHT for [bold blue]"+ data_dict['name']+ "[/bold blue]")

    packed_dict = msgpack.packb(data_dict)
    node.put(dht.InfoHash.get(my_unique_key), dht.Value(packed_dict))

    new_dict = {
        "friends": [
            hashlib.md5("another_friend".encode('utf-8')).hexdigest()
        ]
    }
    packed_dict = msgpack.packb(new_dict)
    # node.put(dht.InfoHash.get(unique_key), dht.Value(packed_dict))

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
    console.print(":sparkles:", "Putting dict on DHT for [bold blue]"+ data_dict['name']+ "[/bold blue]")

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
    console.print(":sparkles:", "Putting dict on DHT for [bold blue]"+ data_dict['name']+ "[/bold blue]")

    packed_dict = msgpack.packb(data_dict)
    node.put(dht.InfoHash.get(uunique_key), dht.Value(packed_dict))

    # Dr. Wu
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
    console.print(":sparkles:", "Putting dict on DHT for [bold blue]"+ data_dict['name']+ "[/bold blue]")

    # print("Putting dict on DHT: ", data_dict)
    packed_dict = msgpack.packb(data_dict)
    node.put(dht.InfoHash.get(wunique_key), dht.Value(packed_dict))

# Retrieve


def find_friends(root: str, state: list, depth: int, target_depth: int, friends_visited: set) -> dict:
    state = []
    friends_visited.add(root)
    results = node.get(dht.InfoHash.get(root))
    if results:
        to_check = []
        r = msgpack.unpackb(results[0].data)
        friends = r["friends"]
        for friend in friends:
            if not friend in friends_visited:
                friends_visited.add(friend)
                to_check.append(friend)
                inner_results = node.get(dht.InfoHash.get(friend))
                if results:
                    inner_r = msgpack.unpackb(inner_results[0].data)
                    inner_r["depth"] = depth
                    state.append(inner_r)
        if depth < target_depth:
            for friend in to_check:
                state.extend(find_friends(friend, state, depth + 1, target_depth, friends_visited))
    return state
def friendly_depth(depth: int) -> str:
    depth = str(depth)
    if depth[-1] == '1':
        depth += 'st'
    elif depth[-1] == '2':
        depth += 'nd'
    elif depth[-1] == '3':
        depth += 'rd'
    else:
        depth += 'th'
    return f"[purple bold]({depth} connection)"

def walk_tree_friends(tree_root: Tree, root: str, state: list, depth: int, target_depth: int, friends_visited: set) -> dict:
    state = []
    results = node.get(dht.InfoHash.get(root))
    if results:
        to_check = []
        r = msgpack.unpackb(results[0].data)
        new_branch = tree_root.add(f"[blue bold] :bust_in_silhouette: {r['name']} [/blue bold]{friendly_depth(depth)}")
        pkgs = new_branch.add('[yellow bold]:gear: Packages')
        for pkg in r['packages']:
            pkgs.add(':package: ' + pkg)
        friends = r["friends"]
        for friend in friends:
            if not friend in friends_visited:
                friends_visited.add(friend)
                to_check.append(friend)
                inner_results = node.get(dht.InfoHash.get(friend))
                if results:
                    inner_r = msgpack.unpackb(inner_results[0].data)
                    inner_r["depth"] = depth
                    state.append(inner_r)
        if depth < target_depth:
            for friend in to_check:
                state.extend(walk_tree_friends(new_branch, friend, state, depth + 1, target_depth, friends_visited))
    return state

def fetch_pypi(package: str) -> Optional[str]:
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    # response.raise_for_status()
    # access JSOn content
    # print(response.json()['info'])
    if response.status_code == requests.codes.ok:
        json_response = response.json()
        project_urls =  json_response['info']['project_urls']
        # print(json_response['info']['project_urls'])
        return project_urls.get('Github', project_urls.get('Source', project_urls.get('Source Code', project_urls.get('Homepage', 'NOT_FOUND'))))
    else:
        return 'NOT_FOUND'

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
    if "github.com" in package_git:
        stars, forks = fetch_github(package_git[-2], package_git[-1])
    else:
        stars, forks = 0, 0
    if package == 'json-rc':
        # NOTE: THIS IS FOR THE DEMO ONLY!
        # This is supposed to be a fake package that has had its
        # Github stats faked (bots forking/starring)
        stars, forks = 412, 34
    if ct > 0.0:
        return ((ct * 1/d), (forks * stars), stars, forks)
    else:
        return (0, (forks * stars), stars, forks)


# https://pypi.org/pypi/sampleproject/json

social_scores = {}
# print(friends)
node.bootstrap("bootstrap.jami.net", "4222")

# for friend in friends:
#     for package in friend['packages']:
#         package_git = fetch_pypi(package).split('/')
#         stars, forks = fetch_github(package_git[-2], package_git[-1])
#         social_scores[package] = friend['depth'] * forks * stars
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('args', nargs='+')
    args = parser.parse_args().args
    if args[0] in ('pip', 'poetry'):
        if len(args) > 2 and args[1] == 'install':
            # bootstrap()

            package = args[2]
            results = node.get(dht.InfoHash.get(my_unique_key)) # packed_dict
            for r in results:
                first = msgpack.unpackb(r.data)
                # print("Found entry: ", first)
                # print("Searching for friends")
                friends = first["friends"]
                for f in friends:
                    result = node.get(dht.InfoHash.get(f))[0]
                    friend_dict = msgpack.unpackb(result.data)
                    # print(friend_dict)

            social_score, github_score, stars, forks = generateScore(package, wunique_key)
            social_score = social_score * 100
            question = lambda q: input(q).lower().strip()[0] == "y"
            console.print(":sparkles:", f"The package '{package}' has a social score of {social_score:,} and a [purple] Github[/purple] score of {github_score:,}.")
            if social_score > 50:
                console.print(f":evergreen_tree: [bold green]Social score higher than 0.5")
            elif social_score < 50 and social_score > 20:
                console.print(f":evergreen_tree: [bold orange]Social score lower than 0.5 but higher than 0.2")
            else:
                console.print(f":evergreen_tree: [bold red]Warning: Social score lower than 0.2")
            console.print(f"[purple]  {forks:,} forks on Github")
            console.print(f"[purple]  {stars:,} stars on Github")
            if question("Are you sure you want to proceed? Y/n"):
                console.print(":sparkles:", f"Installing package '{package}':")
                if not package in data_dict['packages']:
                    data_dict['packages'].append(package)
                    packed_dict = msgpack.packb(data_dict)
                    node.put(dht.InfoHash.get(my_unique_key), dht.Value(packed_dict))
                # subprocess.run(list(args))
                # TODO: add installed package to the user's DHT entry
            else:
                console.print(":sparkles:", "Installation aborted")
        else:
            subprocess.run(list(args))
    elif args[0] == 'packages':
        # bootstrap()
        hash_friend = hashlib.md5(args[1].encode('utf-8')).hexdigest()
        results = node.get(dht.InfoHash.get(hash_friend))
        if results:
            unpackd = msgpack.unpackb(results[0].data)
            friend_tree = Tree(':bust_in_silhouette: '+ args[1])
            for pkg in unpackd['packages']:
                friend_tree.add(':package: ' + pkg)
            console.print(friend_tree)
        else:
            console.print(f"[red] No friend found for {args[1]}")
    elif args[0] == 'add':
        with console.status("[bold blue]Adding friend to graph...", spinner='moon') as status:
            hash_friend = hashlib.md5(args[1].encode('utf-8')).hexdigest()
            data_dict['friends'].append(hash_friend)
            packed_dict = msgpack.packb(data_dict)
            console.print(":sparkles:", "Calculated hash for friend ", args[1],": ", hash_friend)
            node.put(dht.InfoHash.get(my_unique_key), dht.Value(packed_dict))
            console.print(":sparkles:","Added friend to social graph")
    elif args[0] == 'tree':
        # bootstrap()
        tree = Tree("[green bold]:evergreen_tree: Social tree")
        walk_tree_friends(tree, wunique_key, [], 1, 100, set())
        console.print(tree)
    elif args[0] == 'bootstrap':
        bootstrap()
    else:
        console.print(":red_circle: This command or  package manager is not supported yet. Sorry.")

# TODO:
"""
- It needs a name: spm (social package manager) ?
- The packages are hard coded. When a user runs spm install x, it should add x to their hash table entry
- The calculation sucks and isn't correct, it needs to weight the amount of friends and friends of friends.
- Github stats should weigh less
- the ui could be improved
- we need a demo that shows how it works across several machines
"""