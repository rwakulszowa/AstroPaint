import uuid

import numpy as np

import astropaint.base


class Analyzed(object):
    def __init__(self, model, params, id=None):
        self.model = model
        self.params = params
        self.id = id or uuid.uuid4().hex

    def dictify(self):
        return {
            "model": self.model.__dict__,
            "params": self.params,
            "id": self.id
        }


class Analyzer(object):
    PARAMS = ["mean", "quantiles"]

    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def execute(self):
        model = ModelPicker(self.db, self.raw).pick()
        params = self._analyze(model)
        analyzed = Analyzed(model, params)
        self._put_into_db(analyzed)
        return analyzed

    def _put_into_db(self, o):
        return self.db.put_analyzed(o)

    def _analyze(self, model):
        return {param: self._compute(param) for param in model.params}

    def _compute(self, param):
        return {
            "mean": self._compute_mean,
            "quantiles": self._compute_quantiles
        }.get(param)()

    def _compute_mean(self):
        return self.raw.data.mean()

    def _compute_quantiles(self):
        return list(np.percentile(self.raw.data, range(20, 100, 20)))


class Model(object):
    def __init__(self, params, kind):
        self.params = params
        self.kind = kind


class ModelPicker(astropaint.base.BasePicker):
    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def _pick_dumb(self):
        return Model(["mean", "quantiles"], "ANY")
