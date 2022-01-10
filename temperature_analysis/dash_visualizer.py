from dash_core_components import Graph, Tabs, Tab, Loading
from dash_html_components import Div
from dash_table import DataTable
from numpy import arange
from plotly.subplots import make_subplots
from plotly.express import bar, box, density_heatmap, histogram

from temperature_analysis.abstractions import ACF, ADF, Correlations, OverLimited, PACF, Mean, NormalTest


class DashVisualizer:
    template: str
    height: int

    def __init__(self, template: str, *, height: int = 800):
        self.template = template
        self.height = height

    def layout(self) -> Div:
        return Div([
            Tabs(
                id='tabs',
                value='acf-tab',
                children=[
                    Tab(
                        label='ACF',
                        value='acf-tab'
                    ),
                    Tab(
                        label='PACF',
                        value='pacf-tab'
                    ),
                    Tab(
                        label='Корреляции',
                        value='corr-tab'
                    ),
                    Tab(
                        label='Не по ГОСТу',
                        value='over-limit-tab'
                    ),
                    Tab(
                        label='Распределение',
                        value='distribution-tab'
                    ),
                    Tab(
                        label='Описание',
                        value='description-tab'
                    ),
                    Tab(
                        label='Тест Шапиро-Уилка',
                        value='normal-tab'
                    ),
                    Tab(
                        label='Тест Дики-Фуллера',
                        value='adf-tab'
                    )
                ]
            ),
            Loading(
                id="tab-content",
                type="default",
                fullscreen=True
            )
        ])

    def cf(self, data: ACF or PACF, names: list[str], title: str) -> Graph:
        figure = make_subplots(rows=len(data), subplot_titles=names)

        for i, row in enumerate(data):
            x = arange(len(row[0]))
            figure.add_bar(
                x=x,
                y=row[0],
                showlegend=False,
                name=names[i],
                row=i + 1,
                col=1
            )
            figure.add_scatter(
                x=x,
                y=row[1][:, 1] - row[0],
                mode='lines',
                line_color='rgba(0, 0, 0, 0)',
                showlegend=False,
                name=f'▲{names[i]}',
                row=i + 1,
                col=1
            )
            figure.add_scatter(
                x=x,
                y=row[1][:, 0] - row[0],
                mode='none',
                showlegend=False,
                fill='tonextx',
                name=f'▼{names[i]}',
                row=i + 1,
                col=1
            )

        figure.update_layout(
            title=title,
            template=self.template,
            height=self.height
        )

        return Graph(figure=figure)

    def corr(self, data: Correlations, names: list[str]) -> Graph:
        figure = make_subplots(rows=len(names), cols=len(names))

        for i, x_col in enumerate(names):
            for j, y_col in enumerate(names):
                figure.add_scatter(
                    x=data[x_col][y_col].index,
                    y=[round(value, 2) for value in data[x_col][y_col]],
                    mode='lines',
                    name=f'{x_col}, {y_col}',
                    row=i + 1,
                    col=j + 1
                )

        figure.update_layout(
            title='Корреляция',
            template=self.template,
            height=self.height
        )

        return Graph(figure=figure)

    def over_limit(self, data: OverLimited) -> Graph:
        return Graph(
            figure=bar(
                data,
                title='Статистика выходов температуры помещений за рамки ГОСТа',
                labels={
                    'index': 'Дата',
                    'value': 'Кол-во замеров темп. вне ГОСТа',
                    'variable': 'Граница ГОСТа'
                },
                template=self.template,
                height=self.height
            )
        )

    def dist(self, data: Mean, mode: str = 'histogram') -> Graph:
        if mode == 'heatmap':
            return Graph(
                figure=density_heatmap(
                    data,
                    marginal_y='box',
                    title='Распределение температур по месяцам',
                    labels={
                        'index': 'Месяц',
                        'variable': 'Кабинет',
                        'value': 'Температура'
                    },
                    template=self.template,
                    height=self.height
                ).update_layout(
                    coloraxis_colorbar_title=''
                )
            )
        elif mode == 'box':
            return Graph(
                figure=box(
                    data,
                    title='Распределение температур по кабинетам',
                    labels={
                        'index': 'Месяц',
                        'variable': 'Кабинет',
                        'value': 'Температура'
                    },
                    template=self.template,
                    height=self.height
                )
            )
        else:
            return Graph(
                figure=histogram(
                    data,
                    barmode='overlay',
                    title='Распределение температур по кабинетам',
                    labels={
                        'index': 'Месяц',
                        'variable': 'Кабинет',
                        'value': 'Температура'
                    },
                    template=self.template,
                    height=self.height
                ).update_layout(
                    yaxis_title='Количество'
                )
            )

    def description(self, data: Mean) -> DataTable:
        df = data.describe().reset_index().rename(columns={'index': 'Аудитория'})

        return DataTable(
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={'height': f'{self.height}px'}
        )

    def test(self, data: ADF or NormalTest) -> DataTable:
        df = data.reset_index().rename(columns={
            'index': 'Аудитория',
            'statistic': 'Значение статистики',
            'pvalue': 'P-value'
        })

        return DataTable(
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={'height': f'{self.height}px'}
        )
