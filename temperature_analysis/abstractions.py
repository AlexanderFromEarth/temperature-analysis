from typing import Protocol, NewType

from pandas import DataFrame


OverLimited = NewType('OverLimited', DataFrame)
Mean = NewType('Mean', DataFrame)
NormalTest = NewType('NormalTest', DataFrame)
Correlations = NewType('Correlations', dict)
ACF = NewType('ACF', list)
PACF = NewType('PACF', list)
ADF = NewType('ADF', DataFrame)


class Fetcher(Protocol):
    def fetch(self, *, filter_: bool = True, part_: str = 'wall') -> DataFrame: ...
