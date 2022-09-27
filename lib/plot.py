import numpy as np

class Line:
    def __init__(self, title: str, x: list, y: list, labels: list, legend: bool = False):
        self.title = title
        self.x = x
        self.y = y
        self.labels = labels
        self.legend = legend

    def plot(self):
        legend = {
            "data": self.labels,
            "show": self.legend,
            "top": "10%"
        }
        series = [{
            "name": i[1],
            "data": self.y[i[0]],
            "type": "line",
            "symbol": "none"
        } for i in enumerate(self.labels)]
        
        option = {
            "title":{"text": self.title},
            "legend": legend,
            "tooltip":{"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": self.x
            },
            "yAxis": {"type": "value"},
            "series": series
        }

        return option


class LineForecast:
    def __init__(self, title: str, x: list, y: list, betweenes_index: int, labels: list, legend: bool = False, base_color='blue', forecast_color='red'):
        self.title = title
        self.x = x
        self.y = y
        self.labels = labels
        self.legend = legend
        self.base_col = base_color
        self.forecast_col = forecast_color
        self.betweenes_index = betweenes_index # based on index of DOC

    def __get_visual_map(self):
        pieces = [{
            "lte": self.betweenes_index,
            "color": self.base_col
        }, {
            "gt": self.betweenes_index,
            "lte": len(self.y[0]),
            "color": self.forecast_col
        }]

        return {
            "show": False,
            "dimension": 0, 
            "pieces": pieces
        }


    def plot(self):
        legend = {
            "data": self.labels,
            "show": self.legend,
            "top": "10%"
        }
        series = [{
            "name": i[1],
            "data": self.y[i[0]],
            "type": "line",
            "symbol": "none",
            "markArea": {
                "itemStyle": {
                    "color": "#f4f5fb"
                },
                "data": [
                    [
                        {
                            "name": "forecast",
                            "xAxis": self.betweenes_index
                        },{
                            "xAxis": self.x[-1]
                        }
                    ]
                ]
            }
        } for i in enumerate(self.labels)]
        
        option = {
            "title":{
                "text": self.title,
                "left": "center"
            },
            "legend": legend,
            "tooltip":{"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": self.x
            },
            "yAxis": {"type": "value"},
            "visualMap": self.__get_visual_map(),
            "series": series
        }

        return option

class Pie:
    def __init__(self, title, data, douhgnut: bool = False, legend: bool = False) -> None:
        self.title = title
        self.data = data
        self.doughnut = douhgnut
        self.legend = legend

    def plot(self):
        radius = ['40%', '70%'] if self.doughnut else '50%'
        option = {
            "title": {
                "text": self.title
            },
            "legend": {"show": self.legend},
            "tooltip": {
                "trigger": 'item'
            },
            "series": [
                {
                    "name": 'Costing',
                    "type": 'pie',
                    "radius": radius,
                    "data": self.data,
                    "emphasis": {
                        "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        }
        return option


class LineScatter:
    def __init__(self, title: str, x: list, y: list, absis: list, ordinat: list, labels=["line", "scatter"]):
        self.title = title
        self.absis_scatter = np.array(absis)
        self.ordinat_scatter = np.array(ordinat)
        self.x = x
        self.y = y
        self.labels = labels

    def plot(self):
        series = [{
            "name": self.labels[0],
            "data": self.y,
            "type": "line",
            "symbol": "none"
        }, {
            "name": self.labels[1],
            # "data": np.append(self.absis_scatter.reshape(self.absis_scatter.size,1), 
            #         self.ordinat_scatter.reshape(self.ordinat_scatter.size,1), axis=1).tolist(),
            "data": np.append(np.array(list(range(len(self.x)))).reshape(len(self.x), 1), 
                    self.ordinat_scatter.reshape(self.ordinat_scatter.size,1), axis=1).tolist(),
            "type": "scatter"
        }]
        
        option = {
            "title":{"text": self.title},
            "tooltip":{"trigger": "axis"},
            "legend":{},
            "yAxis": {"type": "value"},
            "xAxis": {
                "type": "category",
                "data": self.x
            },
            "series": series
        }

        return option

class Scatter:
    def __init__(self, title: str, absis: list, ordinat: list):
        self.title = title
        self.absis_scatter = np.array(absis)
        self.ordinat_scatter = np.array(ordinat)

    def plot(self):

        series = [{
            "name": "scatter",
            "symbolSize": 10,
            "data": np.append(self.absis_scatter.reshape(self.absis_scatter.size,1), 
                    self.ordinat_scatter.reshape(self.ordinat_scatter.size,1), axis=1).tolist(),
            "type": "scatter"
        }]

        option = {
            "title":{"text": self.title},
            "tooltip":{"trigger": "axis"},
            "xAxis": {},
            "yAxis": {},
            "series": series
        }


        return option