from dateutil.parser import parse
from functools import lru_cache
from itertools import takewhile
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import get
from pandas import DataFrame, Series, to_numeric

from temperature_analysis.abstractions import Fetcher


class UrlFetcher(Fetcher):
    url: str

    def __init__(self, url: str, *, init_fetch=False, **kwargs):
        self.url = url

        if init_fetch:
            self.fetch(**kwargs)

    @lru_cache(maxsize=10)
    def fetch(self, *, filter_=True, part_='wall') -> DataFrame:
        df = self._fetch_all()

        if filter_:
            df = df[(df.index > '2020-02-29 23:50:00') & (df.index.dayofweek < 6)].between_time('09:00:00', '18:00:00')
        if part_ in ['wall', 'bat']:
            df = df[[column for column in df.columns if column.startswith(part_)]]
            df = df.rename(columns={column: column.replace(part_, '').replace('_', '') for column in df.columns})

        return df

    def _fetch_all(self) -> DataFrame:
        return DataFrame(
            [
                (lambda data: Series(
                    [record[1] for record in data],
                    [parse(record[0]) for record in data],
                    float,
                    '_'.join((tr_place.td.a.text, tr_class.td.text.replace('-', '_')))
                ).apply(
                    func=to_numeric,
                    errors='coerce',
                    downcast='float'
                ).resample(
                    rule='10Min'
                ).mean())([
                    (measurement[:19], measurement[20:])
                    for measurement in get(urljoin(self.url, tr_place.td.a.get('href'))).text.split('\r\n')[:-1]
                ])
                for tr_class in BeautifulSoup(get(self.url).text).find_all('tr')
                for tr_place in (
                    sibling
                    for sibling in takewhile(
                        lambda sibling: not bool(sibling.get('style')),
                        tr_class.find_next_siblings('tr')
                    )
                    if all(not bool(td.get('style')) for td in sibling.find_all('td'))
                )
                if bool(tr_class.get('style'))
            ]
        ).T


if __name__ == '__main__':
    print(UrlFetcher('https://sensors.mwlabs.ru').fetch())
