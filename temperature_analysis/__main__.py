from temperature_analysis.analyzer import Analyzer
from temperature_analysis.dash_visualizer import DashVisualizer
from temperature_analysis.url_fetcher import UrlFetcher
from temperature_analysis.file_fetcher import FileFetcher
from temperature_analysis.app import App


if __name__ == '__main__':
    App(
        DashVisualizer('seaborn'),
        Analyzer(UrlFetcher('https://sensors.mwlabs.ru'))
        # Analyzer(FileFetcher('../data/temperatures/2021-04-12T13:38:31/2_normalized'))
    ).run()
