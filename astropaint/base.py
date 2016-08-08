class BaseObject(object):
    """Base class for all objects stored in the database"""
    def dictify(self) -> dict:
        return {k: v.dictify() if hasattr(v, 'dictify') else v
                for k, v in self.__dict__.items()}

    @classmethod
    def undictify(cls, data: dict) -> "BaseObject":
        raise NotImplementedError


class BasePicker(object):
    def pick(self):
        state = self._get_state()
        return {
            "stub": self._pick_creative
        }[state]()

    def _get_state(self):
        return "stub"

    def _pick_dumb(self):
        raise NotImplementedError
