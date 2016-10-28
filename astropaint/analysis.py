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


class Analyzer(astropaint.base.BaseModule):
    MODELS = {kind: Model(kind, params) for kind, params in [
        ("ANY", ["mean", "percentile_95", "shape"]),
        ("GALAXY", ["mean", "percentile_5", "percentile_95", "shape"]),
        ("CLUSTER", ["mean", "percentile_5", "percentile_95", "object_count"]),
        ("NEBULA", ["mean", "percentile_5"])  #TODO
    ]}

    def build(self, data_in):
        raw = data_in['raw']  #TODO: consider passing unwrapped values
        model = self._pick_model(raw)
        params = self._analyze(model, raw)
        analyzed = Analyzed(model, params, raw)
        logger.debug(analyzed)
        return analyzed

    @staticmethod
    def _pick_model(raw):
        return Analyzer.MODELS[raw.kind]

    def _analyze(self, model, raw):
        return [self._compute(param, raw) for param in model.params]

    def _compute(self, param, raw):
        return {
            "mean": self._compute_mean,
            "object_count": self._compute_object_count,
            "percentile_5": self._compute_percentile_5,
            "percentile_95": self._compute_percentile_95,
            "shape": self._compute_shape
        }[param](raw)

    def _compute_mean(self, raw):
        return raw.data().mean()

    def _compute_object_count(self, raw):
        data = raw.data()[:, :, 0]
        data = skimage.exposure.equalize_adapthist(data)
        lm = skimage.feature.peak_local_max(data, threshold_abs=np.percentile(data, 95), min_distance=10)
        return len(lm)

    def _compute_percentile_5(self, raw):
        return np.percentile(raw.data(), 5)

    def _compute_percentile_95(self, raw):
        return np.percentile(raw.data(), 95)

    def _compute_shape(self, raw):
        x, y = np.mgrid[:raw.data().shape[0], :raw.data().shape[1]]
        initial = astropy.modeling.models.Gaussian2D(x_stddev=1, y_stddev=1)
        fitter = astropy.modeling.fitting.LevMarLSQFitter()
        fit = fitter(initial, x, y, raw.data()[:, :, 0])
        return fit.x_stddev / fit.y_stddev
