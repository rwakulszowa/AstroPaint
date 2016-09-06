import logging

import astropaint.analysis
import astropaint.classification
import astropaint.db
import astropaint.processing
import astropaint.raw

import config


class App(object):
    def run(self, urls, kind):
        logging.info("Running app for {}".format(urls))
        db = astropaint.db.Db(config.DB_ADDRESS)

        raw = astropaint.raw.Raw(urls, kind=kind, size=(860, 860))
        analyzed = astropaint.analysis.Analyzer(db, raw).execute()
        classed = astropaint.classification.Classifier(db, analyzed, raw).execute()
        processed = astropaint.processing.Processor(db, classed, raw).execute()

        logging.info("Done")
