from collections.abc import MutableMapping


class Poll(MutableMapping):
    def __init__(self, /, **kwargs):
        self.__dict__.update(kwargs)

    def __delitem__(self, key):
        del self.__dict__[key]

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return f"{type(self).__name__}({self.__dict__})"
