import uuid

import sklearn.cluster

import astropaint.base


class Classed(object):
    def __init__(self, layout, cluster, id=None):
        self.layout = layout
        self.cluster = cluster
        self.id = id or uuid.uuid4().hex

    def dictify(self):
        return {
            "layout": self.layout.__dict__,
            "cluster": self.cluster,
            "id": self.id
        }


class Classifier(object):
    def __init__(self, db, analyzed, raw):
        self.db = db
        self.analyzed = analyzed
        self.raw = raw

    def execute(self):
        layout = LayoutPicker(self.db, self.analyzed).pick()
        cluster = 0  #STUB
        classed = Classed(layout, cluster)
        self._put_into_db(classed)
        return classed

    def _put_into_db(self, o):
        return self.db.put_classed(o)

    def _classify(self, layout):
        pass


class Layout(object):
    def __init__(self, clusters, features, kind):
        self.clusters = clusters
        self.features = features
        self.kind = kind


class LayoutPicker(astropaint.base.BasePicker):
    def __init__(self, db, analyzed):
        self.db = db
        self.analyzed = analyzed
        self.max_cluster_count = 3

    def _pick_creative(self):
        model = self.analyzed.model
        analyzed_before = self.db.get_analyzed_by_model(model=model)
        fitter = sklearn.cluster.KMeans(n_clusters=min(self.max_cluster_count,
                                                       len(analyzed_before)))
        data = [a.params for a in analyzed_before]
        fitter.fit(data)
        return Layout(fitter.cluster_centers_.tolist(), model.params, model.kind)

    def _pick_dumb(self):
        return Layout([[0.25], [0.75]], ["mean"], "ANY")
