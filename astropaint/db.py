import couchdb.client

import astropaint.analysis
import astropaint.classification
import astropaint.processing
import astropaint.raw


class Db(object):
    def __init__(self, address):
        self.server = couchdb.client.Server(address)
        self.db = self.server["processing"]

    def put(self, o):
        self._put_dictified(o.dictify(), o.id)

    def get_analyzed_by_model(self, model):
        view = self.db.view("astro/analyzed_by_model", key=model.dictify())
        rows = [self._unpack_row(r.value) for r in view.rows]
        return [astropaint.analysis.Analyzed.undictify(r) for r in rows]

    def get_classed_by_features(self, features):
        view = self.db.view("astro/classed_by_features", key=features)
        rows = [self._unpack_row(r.value) for r in view.rows]
        return [astropaint.classification.Classed.undictify(r) for r in rows]

    def get_processed_evaluated(self):
        view = self.db.view("astro/processed_evaluated", descending=True)
        rows = [self._unpack_row(r.value) for r in view.rows]
        return [astropaint.processing.Processed.undictify(r) for r in rows]

    @classmethod
    def _unpack_row(cls, row):
        values = {k: v for k, v in row.items() if not k.startswith('_')}
        return values

    def _put_dictified(self, object_dict, id):
        self.db[id] = object_dict
