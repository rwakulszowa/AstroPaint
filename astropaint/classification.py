from collections import OrderedDict
import uuid

import sklearn.cluster

import astropaint.base


class Classed(astropaint.base.BaseObject):
    def __init__(self, layout, cluster, id=None):
        self.layout = layout
        self.cluster = cluster
        self.id = id or uuid.uuid4().hex

    @classmethod
    def undictify(cls, data):
        data["layout"] = Layout.undictify(data["layout"])
        return Classed(**data)

    def get_cluster_data(self):
        return {k:v for k, v in zip(self.layout.features, self.layout.clusters[self.cluster])}


class Layout(astropaint.base.BaseObject):
    def __init__(self, clusters, features, kind):
        self.clusters = clusters
        self.features = features
        self.kind = kind

    @classmethod
    def undictify(cls, data):
        return Layout(**data)


class Classifier(object):
    def __init__(self, db, analyzed, raw):
        self.db = db
        self.analyzed = analyzed
        self.raw = raw

    def execute(self):
        layout = LayoutPicker(self.db, self.analyzed).pick()
        cluster = self._classify(self.analyzed, layout)
        classed = Classed(layout, cluster)
        self._put_into_db(classed)
        return classed

    def _put_into_db(self, o):
        return self.db.put_classed(o)

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

    def _get_state(self):  #TODO: do not create new layouts too often
        model = self.analyzed.model
        analyzed_count = len(self.db.get_analyzed_by_model(model=model))
        if analyzed_count < 2 ** len(self.analyzed.params):
            return "unknown"
        else:
            return "learning"

    def _pick_creative(self):
        model = self.analyzed.model
        analyzed_before = self.db.get_analyzed_by_model(model=model)
        clusters_count = 2 ** len(self.analyzed.params)
        fitter = sklearn.cluster.KMeans(n_clusters=clusters_count)
        data = [a.params for a in analyzed_before]
        fitter.fit(data)
        return Layout(sorted(fitter.cluster_centers_.tolist()), model.params, model.kind)

    def _pick_hardcoded(self):
        return Layout([[0.25], [0.75]], ["mean"], "ANY")
