# Используемые технологии

Для выполнения анализа использовались: язык Python 3, среда Anaconda и технология Jupyter Notebook.  
А также стандартная библиотека Python и сторонние библиотеки:

### Для экстракции данных с веб-ресурса:
* **requests** - для отправки запросов по HTTP, является обёрткой над стандартной библиотекой urllib, предоставляющий более
высокоуровневое API
* **bs4** - для парсинга HTML

```python
from itertools import takewhile

from bs4 import BeautifulSoup
from requests import get

base_url = 'https://sensors.mwlabs.ru'
bs = BeautifulSoup(get(base_url).text)

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
```

### Для обработки данных:
* **pandas** - для преобразований временных рядов, имеет большое количество встроенных функций для чтения данных из
различных источников. Используя данную библиотеку можно получить большую производительность нежели используя лишь
стандартную библиотеку
* **statsmodels** - для подсчёта статистик, за счёт встроенных функций для проведения тестов над временнными рядами, для
вычисления характеристик временных рядов в модуле statsmodels.tsa и его подмодулей. Хоть все расчёты можно произвести
с помощью библиотеки NumPy, данный пакет предоставляет готовые функции, что позволит избежать ошибок

```python
from pathlib import Path

from pandas import read_csv
from statsmodels.tsa.stattools import acf




temperatures = read_csv(
    Path() / 'data' / 'temperatures' / 'today' / '2_normalized' / 'dataset.csv',
    parse_dates=True,
    index_col=0
)
monthly_acf = acf(temperatures.bat_420.resample('M').mean(), missing='drop')
```


### Для визуализации:
* **plotly** - в качестве основного инструмента построения визуализаций, аналогом могла выступать уже ставшая стандартом 
в анализе данных библиотека matplotlib, но данный инструмент засчёт более высокой абстракции позволяет визуализировать
данные быстрее, также позволяя делать их интерактивными

```python
from pathlib import Path

from plotly import express as px
from pandas import read_csv


temperatures = read_csv(
    Path() / 'data' / 'temperatures' / 'today' / '2_normalized' / 'dataset.csv',
    parse_dates=True,
    index_col=0
)
resampled = temperatures.resample('D').mean()
px.line(
    resampled,
    resampled.index,
    resampled.columns,
    labels={
        'index': 'Measurement date',
        'value': 'Temperature',
        'variable': 'Sensor'
    },
    template='plotly_dark'
).show()
```

