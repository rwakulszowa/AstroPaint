import os
import urllib.parse

import numpy as np
import requests
import skimage.transform

from astropy.io import fits

import astropaint.base
import astropaint.utils


class Raw(astropaint.base.BaseObject):
    KINDS = ["ANY", "GALAXY", "CLUSTER", "NEBULA"]

    def __init__(self, encoded_urls, kind):
        self.encoded_urls = encoded_urls
        self.kind = kind

    @astropaint.utils.lazy
    def urls(self):
        return [urllib.parse.unquote_plus(e) for e in self.encoded_urls]

    @astropaint.utils.lazy
    def data(self):
        return np.dstack([self._preprocess(self._read(u, "./temp/{}".format(p)), size=(640, 640))  #NOTE: temporarily hardcoded
                          for u, p in zip(self.urls(), self.encoded_urls)])

    def dictify(self):
        return {
            "kind": self.kind,
            "encoded_urls": self.encoded_urls
        }

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


class RawBuilder(object):
    def __init__(self, kind, source_ids, source):
        self.kind = kind
        self.source_ids = source_ids
        self.source = source

    def execute(self):
        return Raw(
            self._make_encoded_urls(self.source_ids, self.source),
            self.kind)

    @classmethod
    def _make_encoded_urls(cls, source_ids, source):
        if source == "encoded_urls":
            return source_ids
        elif source == "raw_urls":
            return [cls._encode(s for s in source_ids)]
        elif source == "HST observations":
            return [cls._encode(cls._build_hst_url(s)) for s in source_ids]
        else:
            raise "unknown source type"

    @staticmethod
    def _encode(url):
        return urllib.parse.quote_plus(url)

    @staticmethod
    def _build_hst_url(obs):
        return "http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID={}_DRZ".format(obs)
