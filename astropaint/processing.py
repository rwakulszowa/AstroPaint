import random
import uuid

import numpy as np
import skimage.io
import skimage.exposure

import astropaint.base


class Processed(object):
    def __init__(self, filter, image_path, evaluation, id=None):
        self.filter = filter
        self.image_path = image_path
        self.evaluation = evaluation
        self.id = id or uuid.uuid4().hex

    def dictify(self):
        return {
            "filter": self.filter.__dict__,
            "image_path": self.image_path,
            "evaluation": self.evaluation,
            "id": self.id
        }


class Processor(object):
    METHODS = [
        {"method": "stretch", "params": [5, 95]},
        {"method": "histeq", "params": []},
        {"method": "adjust_gamma", "params": []}
    ]

    def __init__(self, db, classed, raw):
        self.db = db
        self.classed = classed
        self.raw = raw

    def execute(self):
        filter = FilterPicker(self.db, self.classed).pick()
        image_path = "./temp/{}.png".format(random.randint(0, 100))
        evaluation = [0]  #STUB
        data = self._process(filter)
        self._save(data, image_path)
        processed = Processed(filter, image_path, evaluation)
        self._put_into_db(processed)
        return processed

    @staticmethod
    def _save(data, path):
        skimage.io.imsave(path, data)

    def _put_into_db(self, o):
        return self.db.put_processed(o)

    def _process(self, filter):
        data = self.raw.data
        steps = filter.steps
        for s in steps:
            data = self._apply(data, s)
        return data

    def _apply(self, data, step):
        return {
            "stretch": self._apply_stretch,
            "histeq": self._apply_histeq,
            "adjust_gamma": self._apply_adjust_gamma
        }[step['method']](data, step['params'])

    @staticmethod
    def _apply_adjust_gamma(data, params):
        return np.dstack([
            skimage.exposure.adjust_gamma(d)
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_histeq(data, params):
        return np.dstack([
            skimage.exposure.equalize_hist(d)
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_stretch(data, params):
        return np.dstack([
            skimage.exposure.rescale_intensity(d, in_range=tuple(np.percentile(d, params)))
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])


class Filter(object):
    def __init__(self, steps, kind):
        self.steps = steps
        self.kind = kind


class FilterPicker(astropaint.base.BasePicker):
    def __init__(self, db, classed):
        self.db = db
        self.classed = classed

    def _pick_creative(self):
        kind = self.classed.layout.kind
        methods = Processor.METHODS[:]
        random.shuffle(methods)
        steps = random.sample(methods, random.randint(1, len(methods)))
        return Filter(steps, kind)

    def _pick_dumb(self):
        return Filter([{"method": "stretch", "params": [2, 99.5]}], "ANY")
