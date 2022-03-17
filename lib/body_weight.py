import streamlit as st
from streamlit_echarts import st_echarts

from lib.revenue import aggregation
from lib.plot import Line

BASE_URL = "https://aqua-dinamika.herokuapp.com"

def body_weight_section():
    col1, col2 = st.columns([1, 2])

    with col1:
        t0 = st.number_input("t0", value=0)
        w0 = st.number_input("w0", value=0.05)
        wn = st.number_input("wn", value=75)
        m = st.number_input("m", value=0.0014)
        n0 = st.number_input("n0", value=250)
        area = st.number_input("area", value=314)
        alpha = st.number_input("alpha", value=0.013)
        partial1 = st.number_input("partial1", value=0.1)
        partial2 = st.number_input("partial2", value=0.1)
        partial3 = st.number_input("partial3", value=0.1)
        docpartial1 = st.number_input("doc partial 1", value=60)
        docpartial2 = st.number_input("doc partial 2", value=80)
        docpartial3 = st.number_input("doc partial 3", value=100)
        docfinal = st.number_input("doc final", value=120)

        # opt = st.selectbox("what do you want?", ("body weight", "population"))

        submit = st.button("submit")
    with col2:
        # path = "/plot/body_weight?t0={}&w0={}&wn={}&m={}&n0={}&area={}&alpha={}&partial1={}&partial2={}&partial3={}&docpartial1={}&docpartial2={}&docpartial3={}&docfinal={}".format(
        #     t0, w0, wn, m, n0, area, alpha, partial1, partial2, partial3, docpartial1, docpartial2, docpartial3, docfinal
        # )
        if submit:
            # data = requests.get(BASE_URL+path)
            # data = requests.get(BASE_URL + "/plot/body_weight?t0=0&w0=0.05&wn=75&m=0.0014&n0=250&area=314&alpha=0.013&partial1=0.1&partial2=0.1&partial3=0.1&docpartial1=60&docpartial2=80&docpartial3=100&docfinal=120")
            # st.write(data)
            # st_echarts(options=data.json())
            data = aggregation(t0, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, docpartial1, docpartial2, docpartial3, docfinal)
            index = [t for t in range(t0, docfinal+1)]

            # if str(opt) == "body weight":
            option = Line("Individual weight in gr", index, [data["body_weight"]], ["Wt"]).plot()
            st_echarts(options=option)

            option1 = Line("Population in PL/m2", index, [data["population"]], ["Population"]).plot()
            st_echarts(options=option1)

            option2 = Line("Biomassa", index, [data["biomassa"]], ["Biomassa (kg)"]).plot()
            st_echarts(options=option2)

            option3 = Line("Revenue", index, [data["potential_revenue"], data["realized_revenue"]], 
            ["Potential Revenue", "Realized Revenue"]).plot()
            st_echarts(options=option3)