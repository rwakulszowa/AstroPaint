import numpy as np


#TODO: move utlity-type functions here
def normalize(fun):
    def wrapper(data, params):
        return np.dstack([
            _scale(fun(d, params).astype(float)) for d in [data[:,:,i] for i in range(data.shape[-1])]
        ])
    return wrapper

def lazy(fun):
    def wrapper(self, *args, **kwargs):
        try:
            getattr(self, fun.__name__ + "_")
        except AttributeError:
            setattr(self, fun.__name__ + "_", fun(self, *args, **kwargs))
        return getattr(self, fun.__name__ + "_")
    return wrapper

def _scale(data):
    data -= data.min()
    data *= 1.0 / data.max()
    return data
