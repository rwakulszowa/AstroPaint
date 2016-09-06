from collections import OrderedDict
import uuid

import sklearn.cluster

import astropaint.base


class Classed(astropaint.base.BaseObject):
    def __init__(self, features, layout, cluster, id=None):
        self.features = features
        self.layout = layout
        self.cluster = cluster
        self.id = id or uuid.uuid4().hex

    @classmethod
    def undictify(cls, data):
        data["layout"] = Layout.undictify(data["layout"])
        return Classed(**data)

    def save(self, db):
        db.put_classed(self)

    def get_cluster_data(self):
        return OrderedDict([(k, v) for k, v in zip(self.features, self.layout.clusters[self.cluster])])


class Layout(astropaint.base.BaseObject):
    def __init__(self, clusters):
        self.clusters = clusters

    @classmethod
    def undictify(cls, data):
        return Layout(**data)


class Classifier(object):
    def __init__(self, db, analyzed, raw):
        self.db = db
        self.analyzed = analyzed
        self.raw = raw

    def execute(self):
        layout, state = LayoutPicker(self.db, self.analyzed).pick()
        cluster = self._classify(self.analyzed, layout)
        classed = Classed(self.analyzed.model.params, layout, cluster)
        classed.save(self.db)
        return classed

    @classmethod
    def _classify(cls, analyzed, layout):
        distances = [cls._diff_sum(analyzed.params, c) for c in layout.clusters]
        return distances.index(min(distances))

    @staticmethod
    def _diff_sum(a, b):
        return sum([abs(x - y) for x, y in zip(a, b)])


class LayoutPicker(astropaint.base.BasePicker):
    def __init__(self, db, analyzed):
        self.db = db
        self.analyzed = analyzed
        self.analyzed_before = self.db.get_analyzed_by_model(model=self.analyzed.model)

    def _get_state(self):
        analyzed_count = len(self.analyzed_before)
        threshold = 16
        if analyzed_count < threshold:
            state = "unknown"  #TODO: refactor base.get_state
        elif analyzed_count == threshold:  # build a layout only once
            state = "learning"
        elif analyzed_count > threshold:
            state = "smart"
        return state

    def _pick_best(self):
        classed = self.db.get_classed_by_features(features=self.analyzed.model.params)[0]
        return classed.layout

    def _pick_creative(self):
        model = self.analyzed.model
        clusters_count = 2 ** len(self.analyzed.params)
        fitter = sklearn.cluster.KMeans(n_clusters=clusters_count)
        data = [a.params for a in self.analyzed_before]
        fitter.fit(data)
        return Layout(sorted(fitter.cluster_centers_.tolist()))

    def _pick_hardcoded(self):
        return Layout([[]])
