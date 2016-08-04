import uuid


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
    def __init__(self, db, raw):
        self.db = db
        self.raw = raw

    def execute(self):
        model = DumbModelPicker(self.db, self.raw).pick()
        params = {}  #STUB
        analyzed = Analyzed(model, params)
        self._put_into_db(analyzed)
        return analyzed

    def _put_into_db(self, o):
        return self.db.put_analyzed(o)


class Model(object):
    def __init__(self, params, kind):
        self.params = params
        self.kind = kind


class BaseModelPicker(object):
    def __init__(self, db, raw):
        self.db = db
        self.raw = raw


class DumbModelPicker(BaseModelPicker):
    def pick(self):
        return Model(["mean", "quantiles"], "ANY")