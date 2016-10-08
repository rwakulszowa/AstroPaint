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
        return cls(**data)


class BasePicker(object):
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
