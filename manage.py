import argparse
import couchdb.client

import config


parser = argparse.ArgumentParser()
parser.add_argument(dest="command", help="only cleardb command is supported now :/")


DBS = ["analysis", "classification", "processing"]

def cleardb():
    print("Clearing databases {} in {}".format(DBS, config.DB_ADDRESS))
    server = couchdb.client.Server(config.DB_ADDRESS)
    for db in DBS:
        db = server[db]
        docs = [db[id] for id in db]
        db.purge(docs)


if __name__ == "__main__":
    args = parser.parse_args()
    commands = {
        "cleardb": cleardb
    }
    commands[args.command]()