import argparse
import logging
import sys

import astropaint.app


parser = argparse.ArgumentParser()
parser.add_argument(dest="urls", nargs="+", help="URLs of FITS files to be processed")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == "__main__":
    args = parser.parse_args()
    app = astropaint.app.App()
    app.run(args.urls)
