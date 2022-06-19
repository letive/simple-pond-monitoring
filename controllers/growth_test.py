import streamlit as st
import numpy as np
from lib.growth_function import GrowthFunction

from lib.unit_economic import set_global_variable, cost_structure
from lib.metrices import Compute
from lib.biomass import Biomassa
from lib.plot import Line, Pie
from streamlit_echarts import st_echarts
import pandas as pd

def growth():
    st.title("Growth Rate Test")

    t0 = st.sidebar.number_input("t0", value=0)
    sr = st.sidebar.number_input("survival rate", value=0.92)
    n0 = st.sidebar.number_input("n0", value=100)
    T = st.sidebar.number_input("T", value=120)
        
    area = st.sidebar.number_input("area", value=1000)
    alpha = st.sidebar.number_input("alpha (shrimp growth rate)", value=1.0, step=1.,format="%.2f")/100 

    w0 = st.sidebar.number_input("w0", value=0.05)
    wn = st.sidebar.number_input("wn", value=40)

    partial1 = st.sidebar.number_input("partial1", value=0.1)
    partial2 = st.sidebar.number_input("partial2", value=0.1)
    partial3 = st.sidebar.number_input("partial3", value=0.1)
    
    docpartial1 = int(st.sidebar.number_input("doc partial 1", value=60))
    docpartial2 = int(st.sidebar.number_input("doc partial 2", value=70))
    docpartial3 = int(st.sidebar.number_input("doc partial 3", value=80))
    docfinal = int(st.sidebar.number_input("doc final", value=120))

    
    condition = st.sidebar.expander("Conditional Configuration")
    
    condition.markdown("## Upload Data")
    bio = condition.file_uploader("Biological Data")
    with open("data/data_sample - biological.csv") as f:
        condition.download_button('See the example of biological data', f, file_name='biological.csv')

    chem = condition.file_uploader("Chemical Data")
    with open("data/data_chemical_v2.csv") as f:
        condition.download_button('See the example of chemical data', f, file_name='chemical.csv')


    condition.markdown("## Temperature")
    temp_suitable_min = condition.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = condition.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    
    temp_optimal_min = condition.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = condition.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    # temp_upper_limit = st.sidebar.number_input("Temperature upper limit", value=36.0, step=1.,format="%.2f")
    # temp_weight = st.sidebar.number_input("weight of temperature", value=1.0, step=1.,format="%.2f")  

    condition.markdown("## Dissolved Oxygen")
    do_suitable_min = condition.number_input("DO suitable min", value=4.0, step=1.,format="%.2f") 
    do_suitable_max = condition.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    
    do_optimal_min = condition.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    do_optimal_max = condition.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    # do_upper_limit = st.sidebar.number_input("DO upper limit", value=10.0, step=1.,format="%.2f") 
    # do_weight = st.sidebar.number_input("weight of DO", value=1.0, step=1.,format="%.2f")  

    condition.markdown("## Unionized Ammonia")
    ua_suitable_min = condition.number_input("UA suitable min", value=0.0, step=1.,format="%.2f") 
    ua_suitable_max = condition.number_input("UA suitable max", value=0.16, step=1.,format="%.2f") 
    
    ua_optimal_min = condition.number_input("UA optimal min", value=0.0001, step=1.,format="%.2f") 
    ua_optimal_max = condition.number_input("UA optimal max", value=0.06, step=1.,format="%.2f")

    # ua_upper_limit = st.sidebar.number_input("UA upper limit", value=1.0, step=1.,format="%.2f") 
    # ua_weight = st.sidebar.number_input("weight of UA", value=1.0, step=1.,format="%.2f")  

    condition.markdown("## Critical Steady Crop (CSC)")
    csc_suitable_min = condition.number_input("CSC suitable min", value=0.0, step=1.,format="%.2f") 
    csc_suitable_max = condition.number_input("CSC suitable max", value=0.5, step=1.,format="%.2f") 
    
    csc_optimal_min = condition.number_input("CSC optimal min", value=0.0, step=1.,format="%.2f") 
    csc_optimal_max = condition.number_input("CSC optimal max", value=3.0, step=1.,format="%.2f")

    # csc_upper_limit = st.sidebar.number_input("CSC upper limit", value=7.0, step=1.,format="%.2f") 
    # csc_weight = st.sidebar.number_input("weight of CSC", value=1.0, step=1.,format="%.2f")  

    costing_section = st.sidebar.expander("Costing Configuration")
    e = costing_section.number_input("energy day cost", value=4.0, step=1.,format="%.2f")
    p = costing_section.number_input("daily probiotics", value=120000)
    o = costing_section.number_input("others cost", value=30000)
    labor = costing_section.number_input("labor cost", value=2000000)/30
    bonus = costing_section.number_input("bonus", value=2000)
    h = costing_section.number_input("harvest cost per kg", value=1000)
    r = costing_section.number_input("feeding rate", value=0.04)
    fc = costing_section.number_input("feeding price", value=16000)
    formula = costing_section.selectbox("formula", (1, 2))

    submit = st.sidebar.button("submit")

    if submit:
        if (bio is not None) & (chem is not None):
            set_global_variable(
                temp_suitable_min, 
                temp_suitable_max,
                temp_optimal_min, 
                temp_optimal_max,
                do_suitable_min,
                do_suitable_max,
                do_optimal_min, 
                do_optimal_max,
                ua_suitable_min,
                ua_suitable_max,
                ua_optimal_min,
                ua_optimal_max,
                csc_suitable_min,
                csc_suitable_max,
                csc_optimal_min,
                csc_optimal_max,
                chem,
                bio
                )

           
        else:
            set_global_variable(
                temp_suitable_min, 
                temp_suitable_max,
                temp_optimal_min, 
                temp_optimal_max,
                do_suitable_min,
                do_suitable_max,
                do_optimal_min, 
                do_optimal_max,
                ua_suitable_min,
                ua_suitable_max,
                ua_optimal_min,
                ua_optimal_max,
                csc_suitable_min,
                csc_suitable_max,
                csc_optimal_min,
                csc_optimal_max
                )

        data = cost_structure(t0, T, area, wn, w0, alpha, n0, sr, [partial1, partial2, partial3], [docpartial1, docpartial2, docpartial3], e, p, o, labor, bonus, h, r, fc, formula, docfinal)
        index = [t for t in range(t0, T+1)]

        option_fr = Line("F(r)", index, [data["revenue"]["fr"]], ["F(r)"]).plot()
        st_echarts(options=option_fr)

        option = Line("Individual weight in gr", index, [data["revenue"]["body_weight"]], ["Wt"]).plot()
        st_echarts(options=option)

        partial4 = sr-partial1-partial2-partial3
        if partial4 >= 0:
            option1 = Line("Population", index, [data["revenue"]["population"]], ["Population"]).plot()
            st_echarts(options=option1)

            col1, col2 = st.columns(2)

            with col1:
                option2 = Line("Biomassa", index, [data["revenue"]["biomassa"]], ["Biomassa (kg)"]).plot()
                st_echarts(options=option2)

            with col2:
                option3 = Line("Revenue", index, [data["revenue"]["revenue"], data["revenue"]["potential_revenue"]], 
                ["Realized Revenue", "Potential Revenue"], True).plot()
                st_echarts(options=option3)

            col11, col12 = st.columns(2)
            with col11:
                dataviz = [{"value": i[1], "name": data["index"][i[0]]} for i in enumerate(data["aggregate"])]
                option4 = Pie("Cost Structure Diagram", dataviz, True).plot()
                st_echarts(options=option4)
            with col12:
                # profit
                option5 = Line("Profit Margin", index, [data["data_profit"]["revenue"], data["data_profit"]["cost"], data["data_profit"]["profit"]],
                        ["Revenue", "Expense", "Profit"], True).plot()
                st_echarts(options=option5)            
        # else:
        #     st.warning("Error. Maybe the system is error or you didn't upload data yet")