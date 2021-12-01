from argparse import ArgumentParser
from itertools import takewhile
from os import mkdir
from pathlib import Path

from bs4 import BeautifulSoup
from requests import get


def download_data(url: str, path_to_data: str) -> None:
    html = get(url).text
    parsed_html = BeautifulSoup(html, 'html.parser')
    directory_path = f'{Path.cwd()}/{path_to_data}/{parsed_html.text[:19]}'

    mkdir(directory_path)

    for filename, fetch_url in {
        f'{tr.td.text}{tr_local.td.a.text}': f'{url}{tr_local.td.a.get("href")}'
        for tr in parsed_html.find_all('tr')
        for tr_local in (
            tr_sibling
            for tr_sibling in takewhile(
                lambda sibling: not bool(sibling.get('style')),
                tr.find_next_siblings('tr')
            )
            if all(
                not bool(td.get('style'))
                for td in tr_sibling.find_all('td')
            )
        )
        if bool(tr.get('style'))
    }.items():
        with open(f'{directory_path}/{filename}.csv', 'w') as f:
            f.write('\n'.join(f'{ts[:19], ts[21:]}' for ts in get(fetch_url).text.split('\r\n')))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--dir', dest='dir', default='../data/temperatures', help='Directory path')
    parser.add_argument('--url', dest='url', default='http://sensors.mwlabs.ru', help='Url of sensors data')
    args = parser.parse_args()

    download_data(args.url, args.dir)
