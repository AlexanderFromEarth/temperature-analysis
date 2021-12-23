from datetime import datetime
from dateutil.parser import parse
from pathlib import Path


def get_temperatures_path(before: datetime = datetime.now()) -> Path:
    """
    Gets actual measurement date before passed
    :param before: Date before which search starts
    :return: Path to actual measurement data
    :raise RuntimeError: No measurement data for passed date
    """
    temperatures_path = Path.cwd() / '..' / 'data' / 'temperatures'
    measurement_dates = sorted(
        parsed
        for parsed in (
            parse(fetch_date.stem)
            for fetch_date in temperatures_path.iterdir()
        )
        if parsed < before
    )

    if len(measurement_dates) == 0:
        raise RuntimeError

    actual_measurement_date = measurement_dates[-1]

    return temperatures_path / actual_measurement_date.isoformat()
