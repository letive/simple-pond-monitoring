from lib.plot import LineForecast
import numpy as np
from streamlit_echarts import st_echarts

def base():
    x = np.linspace(0, 60).tolist()
    y = np.exp(x).tolist()

    option = LineForecast("test", x, [y], 30, ["test"]).plot()

    st_echarts(
        options=option
    )
