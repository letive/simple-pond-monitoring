from pandas import options
import streamlit as st
from streamlit_echarts import st_echarts

from lib.revenue import aggregation
from lib.plot import Line, Pie
from lib.cost import costing

import numpy as np

BASE_URL = "https://aqua-dinamika.herokuapp.com"

def body_weight_section():
    col1, col2, col3 = st.columns(3)

    with col1:
        t0 = st.number_input("t0", value=0)
        sr = st.number_input("survival rate", value=0.92)
        n0 = st.number_input("n0", value=250)
        T = st.number_input("T", value=80)
    with col2:
        st.write("")
        with st.expander("growth params"):
            area = st.number_input("area", value=314)
            alpha = st.number_input("alpha (shrimp growth rate)", value=0.013)
        with st.expander("weigth params"):
            w0 = st.number_input("w0", value=0.05)
            wn = st.number_input("wn", value=75)

    with col3:
        st.write("")

        with st.expander("Partial Harvest"):
            partial1 = st.number_input("partial1", value=30)
            partial2 = st.number_input("partial2", value=80)
            partial3 = st.number_input("partial3", value=100)
            finalpartial = st.number_input("final partial", value=120)
            
            docpartial1 = int(st.number_input("doc partial 1", value=60))
            docpartial2 = int(st.number_input("doc partial 2", value=80))
            docpartial3 = int(st.number_input("doc partial 3", value=100))
            docfinal = int(st.number_input("doc final", value=120))

        with st.expander("Costing Params"):
            e = st.number_input("energy day cost", value=3.14)
            p = st.number_input("daily probiotics", value=109900)
            o = st.number_input("others cost", value=30000)
            labor = st.number_input("labor cost", value=75000)
            bonus = st.number_input("bonus", value=2000)
            h = st.number_input("harvest cost per kg", value=1000)
            r = st.number_input("feeding rate", value=0.037)
            fc = st.number_input("feeding price", value=16000)
            formula = st.selectbox("formula", (1, 2))

        m = -np.log10(sr)/T

    submit = st.button("submit")
    
    if submit:
        data = aggregation(t0, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, finalpartial, docpartial1, docpartial2, docpartial3, docfinal)
        index = [t for t in range(t0, T+1)]

        option = Line("Individual weight in gr", index, [data["body_weight"]], ["Wt"]).plot()
        st_echarts(options=option)

        if partial1+partial2+partial3+finalpartial == round(n0 * sr):
            option1 = Line("Population in PL/m2", index, [data["population"]], ["Population"]).plot()
            st_echarts(options=option1)
            option2 = Line("Biomassa", index, [data["biomassa"]], ["Biomassa (kg)"]).plot()
            st_echarts(options=option2)
            option3 = Line("Revenue", index, [data["realized_revenue"], data["potential_revenue"]], 
            ["Realized Revenue", "Potential Revenue"]).plot()
            st_echarts(options=option3)

            data = costing(t0, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, finalpartial,
                docpartial1, docpartial2, docpartial3, docfinal, e, p, o, labor, bonus, 
                h, r, fc, int(formula))

            dataviz = [{"value": i[1], "name": data["index"][i[0]]} for i in enumerate(data["aggregate"])]
            option4 = Pie("Cost Structure Diagram", dataviz, True).plot()
            st_echarts(options=option4)

            # profit
            option5 = Line("Profit Margin", index, [data["data_profit"]["revenue"], data["data_profit"]["cost"], data["data_profit"]["profit"]],
                    ["Revenue", "Expense", "Profit"], True).plot()
            st_echarts(options=option5)
        else:
            st.warning("Your partial harvest was wrong")


            