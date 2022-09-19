import streamlit as st
from streamlit_echarts import st_echarts
from lib.plot import LineScatter, Scatter
import numpy as np
import pandas as pd

def base_section():
    
    st.set_page_config(layout="wide")

    st.title("Feeding Regime")