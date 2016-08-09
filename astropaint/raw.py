import os
import urllib.parse

import numpy as np
import requests
import skimage.transform

from astropy.io import fits


class Raw(object):
    KINDS = ["ANY", "GALAXY", "CLUSTER", "NEBULA"]

    def __init__(self, urls, kind, size=None):
        self.urls = urls
        self.encoded_urls = [urllib.parse.quote_plus(u) for u in self.urls]
        self.kind = kind
        self.data = np.dstack([self._preprocess(self._read(u, "./temp/{}".format(p)), size=size)
                               for u, p in zip(self.urls, self.encoded_urls)])


    @classmethod
    def _read(cls, url, path):
        try:
            data = fits.getdata(path)
        except FileNotFoundError:
            with open(path, "wb") as f:
                f.write(requests.get(url).content)
            data = fits.getdata(path)
        return data

    @classmethod
    def _preprocess(cls, image, size):
        image = cls._normalize(image)
        if size:
            image = cls._resize(image, size)
        return image

    @staticmethod
    def _resize(image, size):
        return skimage.transform.resize(image, size)

    @staticmethod
    def _normalize(image):
        image = image.astype(float)
        image -= image.min()
        image *= 1 / image.max()
        return image