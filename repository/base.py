import abc


class BaseRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _init_table(self):
        pass
