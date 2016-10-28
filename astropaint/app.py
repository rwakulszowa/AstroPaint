import logging
import math
import urllib.parse

import astropaint.analysis
import astropaint.classification
import astropaint.db
import astropaint.processing
import astropaint.raw

import config


class App(object):
    def run(self, urls, kind, iterations, source):  #TODO: rename urls param
        logging.info("Running app for {}".format(urls))
        db = astropaint.db.Db(config.DB_ADDRESS)

        # Raw -> assume always succeeds
        raw = astropaint.raw.RawBuilder(
            lambda x: 1,
            db=db,
            max_iter=1
        ).execute(
            kind=kind,
            source_ids=urls,
            source=source)

        # Analyzed -> success if has some params
        analyzed = astropaint.analysis.Analyzer(
            lambda a: 1 if hasattr(a, "params") else -1,
            db=db,
            max_iter=1
        ).execute(
            raw=raw)

        # Classified -> assume always succeeds (for now)  #TODO
        classed = astropaint.classification.Classifier(db, analyzed, raw).execute()

        # Processed -> actually optimize the passed function  #TODO
        for _ in range(iterations):
            processed = astropaint.processing.Processor(db, classed, raw).execute()
            db.put(processed)
        logging.info("Done")
