import couchdb.client

import astropaint.analysis
import astropaint.classification
import astropaint.processing
import astropaint.raw


class Db(object):
    def __init__(self, address):
        self.server = couchdb.client.Server(address)
        self.analysis_db = self.server["analysis"]
        self.classification_db = self.server["classification"]
        self.processing_db = self.server["processing"]

    def put_analyzed(self, o):
        db = self.analysis_db
        self._put_dictified(db, o.dictify())

    def put_classed(self, o):
        db = self.classification_db
        self._put_dictified(db, o.dictify())

    def put_processed(self, o):
        db = self.processing_db
        self._put_dictified(db, o.dictify())

    def get_analyzed_by_model(self, model):
        view = self.analysis_db.view("astro/analyzed_by_model", key=model.dictify())
        rows = [self._unpack_row(r.value) for r in view.rows]
        return [astropaint.analysis.Analyzed.undictify(r) for r in rows]

    def get_processed_evaluated(self):
        view = self.processing_db.view("astro/processed_evaluated", descending=True)
        rows = [self._unpack_row(r.value) for r in view.rows]
        return [astropaint.processing.Processed.undictify(r) for r in rows]

    @classmethod
    def _unpack_row(cls, row):
        values = {k: v for k, v in row.items() if not k.startswith('_')}
        values["id"] = row["_id"]
        return values

    @staticmethod
    def _put_dictified(db, object_dict):
        id = object_dict.pop("id")
        db[id] = object_dict
