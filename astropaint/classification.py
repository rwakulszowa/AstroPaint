import uuid


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
        layout = DumbLayoutPicker(self.db, self.analyzed).pick()
        cluster = 0  #STUB
        classed = Classed(layout, cluster)
        self._put_into_db(classed)
        return classed

    def _put_into_db(self, o):
        return self.db.put_classed(o)


class Layout(object):
    def __init__(self, clusters, kind):
        self.clusters = clusters
        self.kind = kind


class BaseLayoutPicker(object):
    def __init__(self, db, analyzed):
        self.db = db
        self.analyzed = analyzed


class DumbLayoutPicker(BaseLayoutPicker):
    def pick(self):
        return Layout([{"TODO": "pleas"}], "ANY")