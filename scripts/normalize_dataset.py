from argparse import ArgumentParser
from csv import reader
from dateutil.parser import parse
from pathlib import Path
from sys import stdin, stdout

from pandas import DataFrame, Series, to_numeric


def normalize_dataset(in_directory: str = None, out_filename: str = None) -> None:
    input_data = read_files(in_directory) if in_directory else read_cli()
    normalized_dataset = DataFrame([
        Series(
            [record[1] for record in records],
            [parse(record[0]) for record in records],
            name=sensor
        ).apply(
            to_numeric,
            errors='coerce',
            downcast='float'
        ).resample(
            '10Min'
        ).mean() for sensor, records in input_data.items()
    ]).T

    if out_filename:
        to_file(out_filename, normalized_dataset)
    else:
        to_cli(normalized_dataset)


def read_files(directory: str) -> dict:
    directory_path = Path.cwd()/directory

    return {filename.stem: read_file(directory_path/filename) for filename in directory_path.iterdir()}


def read_file(path: Path) -> list:
    with open(path, 'r') as file:
        return [line for line in reader(file)]


def read_cli() -> dict:
    return {
        (tmp := sensor_data.split('\n'))[0]: [line.split(', ') for line in tmp[1:] if line]
        for sensor_data in stdin.read().split('...\n')[:-1]
    }


def to_file(filename: str, dataset: DataFrame) -> None:
    path = Path(filename)

    path.parent.mkdir(parents=True)
    dataset.to_csv(path)


def to_cli(dataset: DataFrame) -> None:
    stdout.write(dataset.to_string())
    stdout.write('\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--in', dest='in_', help='Directory to read data')
    parser.add_argument('--out', dest='out', help='File to save data')
    args = parser.parse_args()

    normalize_dataset(in_directory=args.in_, out_filename=args.out)
