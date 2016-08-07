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
