from dash import Dash
from dash.dependencies import Input, Output

from temperature_analysis.analyzer import Analyzer
from temperature_analysis.dash_visualizer import DashVisualizer


class App:
    app: Dash
    visualizer: DashVisualizer
    model: Analyzer

    def __init__(self, visualizer: DashVisualizer, model: Analyzer):
        self.visualizer = visualizer
        self.model = model
        self.app = Dash(__name__, title='Аналитика температур', update_title='Отрисовываем...')
        self.app.layout = visualizer.layout()

        self.app.callback(
            Output('tab-content', 'children'),
            Input('tabs', 'value')
        )(lambda tab: self.render_content(tab))

    def run(self):
        self.app.run_server()

    def render_content(self, tab: str):
        if tab == 'acf-tab':
            return self.visualizer.cf(self.model.acf, list(self.model.data.columns), 'Автокорреляция')
        elif tab == 'pacf-tab':
            return self.visualizer.cf(self.model.pacf, list(self.model.data.columns), 'Частная автокорреляция')
        elif tab == 'corr-tab':
            return self.visualizer.corr(self.model.correlation, list(self.model.data.columns))
        elif tab == 'over-limit-tab':
            return self.visualizer.over_limit(self.model.over_limit)
        elif tab == 'distribution-tab':
            return self.visualizer.dist(self.model.mean)
        elif tab == 'description-tab':
            return self.visualizer.description(self.model.mean)
        elif tab == 'normal-tab':
            return self.visualizer.test(self.model.normal_test)
        elif tab == 'adf-tab':
            return self.visualizer.test(self.model.adf)
