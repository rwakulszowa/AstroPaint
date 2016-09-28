import argparse
import couchdb.client
import multiprocessing
import PIL.Image
import os

import config


def clear_db():
    print("Clearing databases {} in {}".format(dbs, config.DB_ADDRESS))
    for db in dbs:
        db = server[db]
        docs = [db[id] for id in db if not id.startswith('_')]
        db.purge(docs)

def clear_images():
    print("Clearing images in {}".format(config.STORAGE_DIR))
    for i in _get_images():
        os.remove(os.path.join(config.STORAGE_DIR, i))

def evaluate():
    db = server["processing"]
    ids = [i.split('.')[0] for i in _get_images()]
    for id in ids:
        processed = db[id]
        if processed["evaluation"] is None:
            im = PIL.Image.open(config.STORAGE_DIR + id + ".png")
            im.show()
            e = input("Evaluate {} (0-100):".format(id))
            processed["evaluation"] = (int(e))
            db[id] = processed

def _get_images():
    return [p for p in os.listdir(config.STORAGE_DIR)
              if any(p.endswith(e) for e in [".jpg", ".jpeg", ".png", ".bmp"])]


if __name__ == "__main__":
    commands = {
        "clear_db": clear_db,
        "clear_images": clear_images,
        "evaluate": evaluate,
    }
    dbs = ["analysis", "classification", "processing"]
    server = couchdb.client.Server(config.DB_ADDRESS)

    parser = argparse.ArgumentParser()
    parser.add_argument(dest="command", help="One of: {}".format(list(commands.keys())))

    args = parser.parse_args()
    commands[args.command]()
