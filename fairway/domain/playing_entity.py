from abc import ABC

from fairway.domain.metrics import Metrics


class PlayingEntity(ABC):

    def __init__(self, metrics=Metrics(None, 0, None, 0)):
        self._metrics = metrics

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, metrics):
        self._metrics = metrics

    def reset(self):
        self._metrics = Metrics(None, 0, None, 0)
