from argparse import ArgumentParser
from itertools import takewhile
from pathlib import Path
from urllib.parse import urljoin
from sys import stdout
from typing import Callable

from bs4 import BeautifulSoup
from requests import get


def download_data(directory: str = None) -> None:
    base_url = 'https://sensors.mwlabs.ru'
    html = get(base_url).text
    bs = BeautifulSoup(html, 'html.parser')

    sensors_urls = {
        '_'.join((tr_place.td.a.text, tr_class.td.text.replace('-', '_'))): tr_place.td.a.get('href')
        for tr_class in bs.find_all('tr')
        for tr_place in (
            sibling
            for sibling in takewhile(
                lambda sibling: not bool(sibling.get('style')),
                tr_class.find_next_siblings('tr')
            )
            if all(not bool(td.get('style')) for td in sibling.find_all('td'))
        )
        if bool(tr_class.get('style'))
    }

    handler = path_resolver(directory) if directory else to_cli

    for sensor, url in sensors_urls.items():
        handler(
            sensor,
            '\n'.join(
                f'{ts[:19]}, {ts[20:]}' for ts in get(urljoin(base_url, url)).text.split('\r\n')[:-1]
            )
        )


def path_resolver(directory: str) -> Callable[[str, str], None]:
    directory_path = Path.cwd()/Path(directory)
    directory_path.mkdir(parents=True)

    def to_file(sensor: str, payload: str) -> None:
        with open(directory_path/f'{sensor}.csv', 'w') as f:
            f.write(payload)

    return to_file


def to_cli(sensor: str, payload: str) -> None:
    stdout.write(f'{sensor}\n')
    stdout.write(payload)
    stdout.write('\n')
    stdout.write('...\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--out', dest='out', help='Directory to save data')
    args = parser.parse_args()

    download_data(args.out)
