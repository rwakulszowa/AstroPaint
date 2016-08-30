import json
import random
import uuid

import numpy as np
import scipy.optimize
import skimage.io
import skimage.exposure
import skimage.filters
import skimage.morphology
import sklearn.linear_model
import sklearn.pipeline
import sklearn.preprocessing

import astropaint.base

import config


class Processed(astropaint.base.BaseObject):
    def __init__(self, filter, evaluation, id=None):
        self.filter = filter
        self.evaluation = evaluation
        self.id = id or uuid.uuid4().hex

    @classmethod
    def undictify(cls, data):
        data["filter"] = Filter.undictify(data["filter"])
        return Processed(**data)


class Filter(astropaint.base.BaseObject):
    def __init__(self, steps, kind):
        self.steps = steps
        self.kind = kind

    @classmethod
    def undictify(cls, data):
        return Filter(**data)

    def mutate(self):
        methods = self.get_methods()
        steps = [methods[n].sample() for n in self.get_method_names()]
        random.shuffle(steps)
        return Filter(steps, self.kind)

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
            return random.sample(param, k=1)
        elif domain is "cont":
            return random.uniform(param[0], param[1])


class Processor(object):
    METHODS = [ProcessorMethod(name, params) for name, params in [
        ("stretch", [(0, 5), (98, 100)]),
        ("adjust_gamma", [(0, 2)]),
        ("adjust_log", []),
        ("adjust_sigmoid", [(0, 1)]),
        ("median", [])
    ]]

    def __init__(self, db, classed, raw):
        self.db = db
        self.classed = classed
        self.raw = raw

    def execute(self):
        filter = FilterPicker(self.db, self.classed).pick()
        evaluation = []
        data = self._process(filter)
        processed = Processed(filter, evaluation)
        self._save(data, processed.id)
        self._put_into_db(processed)
        return processed

    @staticmethod
    def _save(data, id):
        path = config.STORAGE_DIR + id + ".png"
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
            "adjust_gamma": self._apply_adjust_gamma,
            "adjust_log": self._apply_adjust_log,
            "adjust_sigmoid": self._apply_adjust_sigmoid,
            "median": self._apply_median,
        }[step['method']](data, step['params'])

    @staticmethod
    def _apply_adjust_gamma(data, params):
        return np.dstack([
            skimage.exposure.adjust_gamma(d, gamma=params[0])
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_adjust_log(data, params):
        return np.dstack([
            skimage.exposure.adjust_log(d)
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_adjust_sigmoid(data, params):
        return np.dstack([
            skimage.exposure.adjust_sigmoid(d, cutoff=params[0])
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_stretch(data, params):
        return np.dstack([
            skimage.exposure.rescale_intensity(d, in_range=tuple(np.percentile(d, params)))
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])

    @staticmethod
    def _apply_median(data, params):
        return np.dstack([
            skimage.filters.median(d, selem=skimage.morphology.disk(3))
            for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])


class FilterPicker(astropaint.base.BasePicker):
    def __init__(self, db, classed):
        self.db = db
        self.classed = classed

    def _get_state(self):
        evaluated = self.db.get_processed_by_kind(kind=self.classed.layout.kind)
        evaluated_count = len(evaluated)
        if evaluated_count < 10:
            return "dumb"
        elif 10 <= evaluated_count < 20:
            return "learning"
        elif 20 <= evaluated_count:
            return "smart"
        else:
            return "unknown"

    def _pick_best(self):
        coverage = 1.0
        kind = self.classed.layout.kind
        processed = self.db.get_processed_by_kind(kind=kind)
        best_filter = processed[0].filter
        covered_processed = processed[:round(coverage * len(processed))]
        similar_processed = [p for p in covered_processed
                             if p.filter.get_method_names() == best_filter.get_method_names()]
        steps = self._predict_steps(similar_processed)
        return Filter(steps, kind)

    def _predict_steps(self, processed_before, classed_param = None):  #TODO: will accept some kinda parameter of the currently processed item
        best_filter = processed_before[0].filter
        steps = best_filter.steps
        bounds = self._unwrap([m.params for m in best_filter.get_methods().values()])
        Y = [p.evaluation[0] for p in processed_before]
        X = [self._unwrap([s["params"] for s in p.filter.steps]) for p in processed_before]
        model = sklearn.pipeline.Pipeline([('poly', sklearn.preprocessing.PolynomialFeatures(degree=2)),
                                           ('linear', sklearn.linear_model.LinearRegression())])
        model = model.fit(X, Y)
        params = self._optimize(model, bounds, self._unwrap([s["params"] for s in best_filter.steps]))
        optimal_steps = self._wrap_values(steps, params)
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
        coverage = 0.4
        kind = self.classed.layout.kind
        processed = self.db.get_processed_by_kind(kind=kind)
        covered_processed = processed[:round(coverage * len(processed))]
        selected_filter = random.choice(covered_processed).filter
        return selected_filter.mutate()

    def _pick_hardcoded(self):
        return Filter([{"method": "stretch", "params": [2, 99.5]}], "ANY")

    def _pick_random(self):
        kind = self.classed.layout.kind
        methods = Processor.METHODS[:]
        random.shuffle(methods)
        steps = random.sample(methods, random.randint(1, len(methods)))
        steps = [s.sample() for s in steps]
        return Filter(steps, kind)
