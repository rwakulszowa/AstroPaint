import itertools
import json
import random
import uuid
import logging

import numpy as np
import scipy.optimize
import skimage.io
import skimage.exposure
import skimage.filters.rank
import skimage.morphology
import sklearn.linear_model
import sklearn.pipeline
import sklearn.preprocessing

import astropaint.base
import astropaint.classification
import astropaint.utils

import config

logger = logging.getLogger(__name__)


class Processed(astropaint.base.BaseObject):
    def __init__(self, classed, cluster, filter, evaluation, id=None):
        self.classed = classed
        self.cluster = cluster
        self.filter = filter
        self.evaluation = evaluation
        self.id = id or uuid.uuid4().hex

    @classmethod
    def undictify(cls, data):
        data["filter"] = Filter.undictify(data["filter"])
        data["classed"] = astropaint.classification.Classed.undictify(data["classed"])
        return Processed(**data)


class Filter(astropaint.base.BaseObject):
    def __init__(self, steps):
        self.steps = steps

    @classmethod
    def undictify(cls, data):
        return Filter(**data)

    def mutate(self):
        methods = self.get_methods()
        steps = [methods[n].sample() for n in self.get_method_names()]
        random.shuffle(steps)
        return Filter(steps)

    def has_step(self, step):
        return step["method"] in [s["method"] for s in self.steps]

    def get_step(self, step):
        try:
            return next(s for s in self.steps if s["method"] == step)
        except StopIteration:
            return None

    def get_method_names(self):
        return [s["method"] for s in self.steps]

    def get_methods(self):
        method_names = self.get_method_names()
        return {m.name: m for m in Processor.METHODS if m.name in method_names}

    def get_bounds(self):
        steps = self.get_method_names()
        methods = self.get_methods()
        return [methods[s].params for s in steps]


class ProcessorMethod(object):
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def sample(self):
        ans =  {
            "method": self.name,
            "params": [self._sample_param(p) for p in self.params]
        }
        return ans

    @staticmethod
    def _sample_param(param):
        domain = "fixed" if type(param) is set else "cont"
        if domain is "fixed":
            return random.sample(param, k=1)[0]
        elif domain is "cont":
            return random.uniform(param[0], param[1])


class Processor(object):
    METHODS = [ProcessorMethod(name, params) for name, params in [
        ("stretch", [(0, 10), (90, 100)]),
        ("adjust_gamma", [(0.5, 2)]),
        ("adjust_log", []),
        ("adjust_sigmoid", [(0, 1)]),
        ("median", [{i for i in range(1, 10)}]),
        ("sharpen_laplace", [(0, 0.25)]),
        ("sharpen_gaussian", [(0, 0.25)])
    ]]

    def __init__(self, db, classed, raw):
        self.db = db
        self.classed = classed
        self.raw = raw

    def execute(self):
        filter, state = FilterPicker(self.db, self.classed).pick()
        logger.debug("State: {}".format(state))
        evaluation = None
        data = self._process(filter)
        processed = Processed(self.classed, self.classed.get_cluster_data(), filter, evaluation)
        self._save_image(data, processed.id)
        logger.debug(processed)
        return processed

    @staticmethod
    def _save_image(data, id):
        path = config.STORAGE_DIR + id + ".png"
        skimage.io.imsave(path, data)

    def _process(self, filter):
        data = self.raw.data()
        steps = filter.steps
        for s in steps:
            data = self._apply(data, s)
        return data

    def _apply(self, data, step):
        return {
            "stretch": self._apply_stretch,
            "adjust_gamma": self._apply_adjust_gamma,
            "adjust_log": self._apply_adjust_log,
            "adjust_sigmoid": self._apply_adjust_sigmoid,
            "autolevel": self._apply_autolevel,
            "median": self._apply_median,
            "sharpen_laplace": self._apply_sharpen_laplace,
            "sharpen_gaussian": self._apply_sharpen_gaussian
        }[step['method']](data, step['params'])

    @staticmethod
    @astropaint.utils.normalize
    def _apply_adjust_gamma(data, params):
        return skimage.exposure.adjust_gamma(data, gamma=params[0])

    @staticmethod
    @astropaint.utils.normalize
    def _apply_adjust_log(data, params):
        return skimage.exposure.adjust_log(data)

    @staticmethod
    @astropaint.utils.normalize
    def _apply_adjust_sigmoid(data, params):
        return skimage.exposure.adjust_sigmoid(data, cutoff=params[0])

    @staticmethod
    @astropaint.utils.normalize
    def _apply_equalize_adapthist(data, params):
        return skimage.exposure.equalize_adapthist(data)

    @staticmethod
    @astropaint.utils.normalize
    def _apply_autolevel(data, params):
        return skimage.filters.rank.autolevel(data)

    @staticmethod
    @astropaint.utils.normalize
    def _apply_stretch(data, params):
        return skimage.exposure.rescale_intensity(data, in_range=tuple(np.percentile(data, params)))

    @staticmethod
    @astropaint.utils.normalize
    def _apply_median(data, params):
        return skimage.filters.rank.median(data, selem=skimage.morphology.disk(params[0]))

    @staticmethod
    @astropaint.utils.normalize
    def _apply_sharpen_laplace(data, params):
        return data + params[0] * (data - skimage.filters.laplace(data, ksize=3))

    @staticmethod
    @astropaint.utils.normalize
    def _apply_sharpen_gaussian(data, params):
        return data + params[0] * (data - skimage.filters.gaussian(data, sigma=1))


class FilterPicker(astropaint.base.BasePicker):
    def __init__(self, db, classed):
        self.db = db
        self.classed = classed
        self.evaluated = self.db.get_processed_evaluated()
        self.evaluated_within_cluster = [e for e in self.evaluated if e.cluster == self.classed.get_cluster_data()]

    def _get_state(self):
        evaluated_count = len(self.evaluated)
        within_cluster_count = len(self.evaluated_within_cluster)
        blueprint = self._get_blueprint()
        if evaluated_count < 20:
            state = "dumb"
        elif 20 <= evaluated_count < 40 or within_cluster_count < 1 or blueprint.evaluation < 20:
            state = "learning"
        elif 40 <= evaluated_count:
            state = "smart"
        return state

    def _get_blueprint(self):
        if len(self.evaluated_within_cluster) > 0:
            blueprint = self.evaluated_within_cluster[0]
        elif len(self.evaluated) > 0:
            blueprint = self.evaluated[0]
        else:
            blueprint = None
        return blueprint

    def _pick_best(self):
        blueprint = self._get_blueprint()
        similar_processed = [p for p in self.evaluated_within_cluster
                             if p.filter.get_method_names() == blueprint.filter.get_method_names()]
        if len(similar_processed) > 0:
            steps = self._predict_steps(similar_processed)
        else:
            steps = blueprint.filter.steps
        return Filter(steps)

    def _predict_steps(self, processed):
        best_filter = processed[0].filter
        bounds = self._unwrap(best_filter.get_bounds())
        Y = [p.evaluation for p in processed]
        X = [self._unwrap([s["params"] for s in p.filter.steps]) for p in processed]
        model = sklearn.pipeline.Pipeline([('poly', sklearn.preprocessing.PolynomialFeatures(degree=2)),
                                           ('linear', sklearn.linear_model.LinearRegression())])
        model = model.fit(X, Y)
        params = self._optimize(model, bounds, self._unwrap([s["params"] for s in best_filter.steps]))
        optimal_steps = self._wrap_values(best_filter.steps, params)
        return optimal_steps

    @staticmethod
    def _unwrap(arr):
        ans = []
        for a in arr:
            ans.extend(a)
        return ans

    @staticmethod
    def _wrap_values(steps, values):
        steps = steps.copy()
        values = iter(values)
        for s in steps:
            for i, _ in enumerate(s["params"]):
                s["params"][i] = next(values)
        return steps

    @staticmethod
    def _optimize(model, bounds, initial_guess):
        def fun(X):
            return -model.predict(X.reshape(1, -1))
        res = scipy.optimize.minimize(fun, initial_guess, bounds=bounds)
        return res.x

    def _pick_creative(self):
        return self._get_blueprint().filter.mutate()

    def _pick_hardcoded(self):
        return Filter([{"method": "stretch", "params": [2, 99.5]}], "ANY")

    def _pick_random(self):
        methods = Processor.METHODS[:]
        random.shuffle(methods)
        steps = random.sample(methods, random.randint(1, len(methods)))
        steps = [s.sample() for s in steps]
        return Filter(steps)
