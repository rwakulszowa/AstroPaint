import numpy as np

from astropy.io import fits


class Raw(object):
    KINDS = ["ANY", "GALAXY", "CLUSTER", "NEBULA"]

    def __init__(self, urls, kind):
        self.urls = urls
        self.kind = kind
        self.data = np.dstack([self._normalize(self._read(u)) for u in self.urls])

    @staticmethod
    def _read(url):
        data = fits.getdata(url, cache=True, show_progress=False)
        return data

    @staticmethod
    def _normalize(image):
        image = image.astype(float)
        image -= image.min()
        image *= 1 / image.max()
        return image