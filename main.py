import argparse
import logging
import sys

import astropaint.app


parser = argparse.ArgumentParser()
parser.add_argument(dest="obs", nargs="+", help="HST observations")
parser.add_argument("-i", "--iterations", default=1, type=int, help="iterations")
parser.add_argument("-k", "--kind", default="ANY", type=str, help="object kind")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def build_hst_url(observation):
    """Converts an observation id to a fits drz file located on http://archives.esac.esa.int/ehst
    """
    return "http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID={}_DRZ".format(observation)

if __name__ == "__main__":
    args = parser.parse_args()
    urls = [build_hst_url(o) for o in args.obs]
    app = astropaint.app.App()
    app.run(urls, args.kind, args.iterations)
