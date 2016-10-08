import argparse
import logging
import sys

import astropaint.app


parser = argparse.ArgumentParser()
parser.add_argument(dest="obs", nargs="+", help="HST observations")
parser.add_argument("-i", "--iterations", default=1, type=int, help="iterations")
parser.add_argument("-k", "--kind", default="ANY", type=str, help="object kind")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


if __name__ == "__main__":
    args = parser.parse_args()
    app = astropaint.app.App()
    app.run(args.obs, args.kind, args.iterations, source="HST observations")
