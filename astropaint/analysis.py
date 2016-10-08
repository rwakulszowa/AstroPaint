import random
import logging

import numpy as np
import astropy.modeling
import skimage.exposure
import skimage.feature

import astropaint.base
import astropaint.raw

logger = logging.getLogger(__name__)


class Analyzed(astropaint.base.BaseObject):
    def __init__(self, model, params, raw):
        self.model = model
        self.params = params
        self.raw = raw

    @classmethod
    def undictify(cls, data):
        data["model"] = Model.undictify(data["model"])
        data["raw"] = astropaint.raw.Raw.undictify(data["raw"])
        return Analyzed(**data)


class Model(astropaint.base.BaseObject):
    def __init__(self, kind, params):
        self.kind = kind
        self.params = params

    @classmethod
    def undictify(cls, data):
        return Model(**data)


class Analyzer(object):
    MODELS = {kind: Model(kind, params) for kind, params in [
        ("ANY", ["mean", "percentile_95", "shape"]),
        ("GALAXY", ["mean", "percentile_5", "percentile_95", "shape"]),
        ("CLUSTER", ["mean", "percentile_5", "percentile_95", "object_count"]),
        ("NEBULA", ["mean", "percentile_5"])  #TODO
    ]}

    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def execute(self):
        model, state = ModelPicker(self.db, self.raw).pick()
        params = self._analyze(model)
        analyzed = Analyzed(model, params, self.raw)
        logger.debug(analyzed)
        return analyzed

    def _analyze(self, model):
        return [self._compute(param) for param in model.params]

    def _compute(self, param):
        return {
            "mean": self._compute_mean,
            "object_count": self._compute_object_count,
            "percentile_5": self._compute_percentile_5,
            "percentile_95": self._compute_percentile_95,
            "shape": self._compute_shape
        }[param]()

    def _compute_mean(self):
        return self.raw.data().mean()

    def _compute_object_count(self):
        data = self.raw.data()[:, :, 0]
        data = skimage.exposure.equalize_adapthist(data)
        lm = skimage.feature.peak_local_max(data, threshold_abs=np.percentile(data, 95), min_distance=10)
        return len(lm)

    def _compute_percentile_5(self):
        return np.percentile(self.raw.data(), 5)

    def _compute_percentile_95(self):
        return np.percentile(self.raw.data(), 95)

    def _compute_shape(self):
        x, y = np.mgrid[:self.raw.data().shape[0], :self.raw.data().shape[1]]
        initial = astropy.modeling.models.Gaussian2D(x_stddev=1, y_stddev=1)
        fitter = astropy.modeling.fitting.LevMarLSQFitter()
        fit = fitter(initial, x, y, self.raw.data()[:, :, 0])
        return fit.x_stddev / fit.y_stddev


class ModelPicker(astropaint.base.BasePicker):
    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def _get_state(self):
        return "smart"

    def _pick_hardcoded(self):
        return Analyzer.MODELS["ANY"]

    def _pick_best(self):
        model = Analyzer.MODELS[self.raw.kind]
        return model
