from collections import OrderedDict


class BaseObject(object):
    """Base class for all objects stored in the database"""
    def dictify(self) -> dict:
        d = self.__dict__
        return OrderedDict([(k, v.dictify() if hasattr(v, 'dictify') else v)
                            for k, v in sorted(d.items())])

    def __repr__(self):
        return str(self.dictify())

    @classmethod
    def undictify(cls, data: dict) -> "BaseObject":
        raise NotImplementedError


class BasePicker(object):
    def pick(self):
        state = self._get_state()
        return {
            "unknown": self._pick_hardcoded,
            "dumb": self._pick_random,
            "learning": self._pick_creative,
            "smart": self._pick_best
        }[state]()

    def _get_state(self):
        return "unknown"  #TODO

    def _pick_hardcoded(self):
        raise NotImplementedError

    def _pick_random(self):
        raise NotImplementedError

    def _pick_creative(self):
        raise NotImplementedError

    def _pick_best(self):
        raise NotImplementedError
