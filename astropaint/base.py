from collections import OrderedDict


class BaseObject(object):
    """Base class for all objects stored in the database"""
    def dictify(self) -> dict:
        d = self.__dict__
        return OrderedDict([(k, v.dictify() if hasattr(v, 'dictify') else v)
                            for k, v in sorted(d.items())])

    def __repr__(self):
        return "{} {}".format(self.__class__,
                              dict(self.dictify()))

    @classmethod
    def undictify(cls, data: dict) -> "BaseObject":
        return cls(**data)


class BasePicker(object):  #TODO get rid of this class
    def pick(self):
        state = self._get_state()
        pick_method = {
            "unknown": self._pick_hardcoded,
            "dumb": self._pick_random,
            "learning": self._pick_creative,
            "smart": self._pick_best
        }[state]
        return pick_method(), state

    def _get_state(self):
        return "unknown"

    def _pick_hardcoded(self):
        raise NotImplementedError

    def _pick_random(self):
        raise NotImplementedError

    def _pick_creative(self):
        raise NotImplementedError

    def _pick_best(self):
        raise NotImplementedError


class BaseModule(object):
    """ Base class for each processing step module

    Each subclass is supposed to provide some complete functionality,
    specified by a obj function.
    The way the obj function gets solved should be hidden inside the module.
    """

    def __init__(self, obj, db=None, max_iter=10):
        self.obj = obj
        self.db = db
        self.max_iter = max_iter

    def execute(self, **kwargs):
        results = [self.build(kwargs) for _ in range(self.max_iter)]
        scores = [self.obj(r) for r in results]
        if all([s < 0 for s in scores]):
            raise Exception("All results suck :/")  #TODO - create an exception class
        else:
            return results[ scores.index(max(scores)) ]
