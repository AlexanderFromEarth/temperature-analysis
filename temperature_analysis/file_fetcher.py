from functools import lru_cache
from pathlib import Path

from pandas import read_csv, DataFrame

from temperature_analysis.abstractions import Fetcher


class FileFetcher(Fetcher):
    path: Path

    def __init__(self, path: str or Path, *, init_fetch=False, **kwargs):
        self.path = Path(path)

        if init_fetch:
            self.fetch(**kwargs)

    @lru_cache(maxsize=10)
    def fetch(self, *, filter_=True, part_='wall') -> DataFrame:
        fn = 'dataset.csv'

        if filter_:
            fn = f'filtered_{fn}'
        if part_ in ['wall', 'bat']:
            fn = f'{part_}_{fn}'

        return read_csv(self.path / fn, parse_dates=True, index_col=0)

