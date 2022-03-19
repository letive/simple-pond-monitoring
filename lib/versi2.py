import streamlit as st
from lib.plot import Line
from lib.dynamic_population import dynamic_poulation
from streamlit_echarts import st_echarts


def version_2():
    col1, col2 = st.columns([1, 2])

    with col1:
        n = st.number_input("the number of partial harvest (n)", value=4)
        n0 = st.number_input("stocking density (n0)", value=314)
        T = st.number_input("maximum days to show (T)", value=120)
        sr = st.number_input("Survival Rate", value=0.9)

        submit = st.button("submit")
        
        
    with col2:
        if submit:
            data, index, p, t = dynamic_poulation(n, n0, sr, T)
            index = list(range(T+1))
            # st.write(data)
            option = Line("Population", index, [data], ["Nt"]).plot()
            st_echarts(options=option)
            
            st.write("Partial Harvest")
            st.write(str(p))
            
            st.write("Partial Time")
            st.write(str(t))