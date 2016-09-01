import argparse
import couchdb.client
import multiprocessing
import PIL.Image
import os

import config


parser = argparse.ArgumentParser()
parser.add_argument(dest="command", help="One of: cleardb, evaluate")


DBS = ["analysis", "classification", "processing"]
SERVER = couchdb.client.Server(config.DB_ADDRESS)

def clear_db():
    print("Clearing databases {} in {}".format(DBS, config.DB_ADDRESS))
    for db in DBS:
        db = SERVER[db]
        docs = [db[id] for id in db if not id.startswith('_')]
        db.purge(docs)

def clear_images():
    print("Clearing images in {}".format(config.STORAGE_DIR))
    for i in _get_images():
        os.remove(os.path.join(config.STORAGE_DIR, i))

def evaluate():
    db = SERVER["processing"]
    ids = [i.split('.')[0] for i in _get_images()]
    for id in ids:
        processed = db[id]
        if len(processed["evaluation"]) == 0:
            im = PIL.Image.open(config.STORAGE_DIR + id + ".png")
            im.show()
            e = input("Evaluate (0-100):")
            processed["evaluation"].append(int(e))
            db[id] = processed

def _get_images():
    return [p for p in os.listdir(config.STORAGE_DIR)
              if any(p.endswith(e) for e in [".jpg", ".jpeg", ".png", ".bmp"])]


if __name__ == "__main__":
    args = parser.parse_args()
    commands = {
        "clear_db": clear_db,
        "clear_images": clear_images,
        "evaluate": evaluate,
    }
    commands[args.command]()