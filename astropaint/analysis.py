import uuid
import random

import numpy as np

import astropaint.base


class Analyzed(astropaint.base.BaseObject):
    def __init__(self, model, params, id=None):
        self.model = model
        self.params = params
        self.id = id or uuid.uuid4().hex

    @classmethod
    def undictify(cls, data):
        data["model"] = Model.undictify(data["model"])
        return Analyzed(**data)

    def save(self, db):
        return db.put_analyzed(self)


class Model(astropaint.base.BaseObject):
    def __init__(self, params, kind):
        self.params = params
        self.kind = kind

    @classmethod
    def undictify(cls, data):
        return Model(**data)


class Analyzer(object):
    PARAMS = {"mean", "percentile_5", "percentile_95"}

    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def execute(self):
        model, state = ModelPicker(self.db, self.raw).pick()
        params = self._analyze(model)
        analyzed = Analyzed(model, params)
        analyzed.save(self.db)
        return analyzed

    def _analyze(self, model):
        return [self._compute(param) for param in model.params]

    def _compute(self, param):
        return {
            "mean": self._compute_mean,
            "percentile_5": self._compute_percentile_5,
            "percentile_95": self._compute_percentile_95
        }[param]()

    def _compute_mean(self):
        return self.raw.data.mean()

    def _compute_percentile_5(self):
        return np.percentile(self.raw.data, 5)

    def _compute_percentile_95(self):
        return np.percentile(self.raw.data, 95)


class ModelPicker(astropaint.base.BasePicker):
    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def _pick_hardcoded(self):
        return Model(["mean", "percentile_95"], "ANY")

    def _pick_random(self):
        #FIXME: params should be picked base on type (i.e. a galaxy will have different available params than a nebula)
        kind = self.raw.kind
        params = sorted(random.sample(Analyzer.PARAMS,
                                      random.randint(1, len(Analyzer.PARAMS))))
        return Model(params, kind)


