from functools import lru_cache

from pandas import DataFrame
from scipy.stats import shapiro
from statsmodels.tsa.stattools import acf, adfuller, pacf

from temperature_analysis.abstractions import ACF, ADF, Correlations, Fetcher, OverLimited, PACF, Mean, NormalTest


class Analyzer:
    fetcher: Fetcher

    def __init__(self, fetcher: Fetcher):
        self.fetcher = fetcher

    @property
    @lru_cache(maxsize=10)
    def adf(self) -> ADF:
        return ADF(DataFrame(
            [
                adfuller(self.mean[column].dropna())[:2]
                for column in self.mean.columns
            ],
            self.mean.columns,
            ['statistic', 'pvalue']
        ))

    @property
    @lru_cache(maxsize=10)
    def pacf(self, *, alpha=0.05) -> PACF:
        return PACF([pacf(self._monthly[column], alpha=alpha) for column in self._monthly.columns])

    @property
    @lru_cache(maxsize=10)
    def acf(self, *, alpha=0.05) -> ACF:
        return ACF([acf(self._monthly[column], missing='drop', alpha=alpha) for column in self._monthly.columns])

    @property
    @lru_cache(maxsize=10)
    def _monthly(self) -> DataFrame:
        return self.data.resample('M').mean()

    @property
    @lru_cache(maxsize=10)
    def correlation(self) -> Correlations:
        return Correlations(
            {
                x_col: {
                    y_col: self.mean[x_col].rolling(90, min_periods=10).corr(self.mean[y_col])
                    for j, y_col in enumerate(self.mean.columns)
                }
                for i, x_col in enumerate(self.mean.columns)
            }
        )

    @property
    @lru_cache(maxsize=10)
    def normal_test(self) -> NormalTest:
        return NormalTest(DataFrame(
            [
               shapiro(self.mean[column].dropna())
               for column in self.mean.columns
            ],
            self.mean.columns,
            ['statistic', 'pvalue']
        ))

    @property
    @lru_cache(maxsize=10)
    def mean(self) -> Mean:
        return Mean(self.data.resample('D').mean().dropna())

    @property
    @lru_cache(maxsize=10)
    def over_limit(self) -> OverLimited:
        return OverLimited(DataFrame(
            [
                self.data.resample('D').agg(lambda x: x[x < 17].count()).sum(axis=1),
                self.data.resample('D').agg(lambda x: x[x > 28].count()).sum(axis=1)
            ],
            ['< 17°C', '> 28°C']
        ).T)

    @property
    def data(self) -> DataFrame:
        return self.fetcher.fetch()
