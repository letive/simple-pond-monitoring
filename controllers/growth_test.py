import streamlit as st
import numpy as np
from lib.growth_function import GrowthFunction
# from lib.partial_harvest import PartialHarvest
from lib.metrices import Compute
from lib.biomass import Biomassa
from lib.plot import Line
from streamlit_echarts import st_echarts
import pandas as pd

def growth():
    st.title("Growth Rate Test")
    st.sidebar.markdown("## Upload Data")
    bio = st.sidebar.file_uploader("Biological Data")
    with open("data/data_sample - biological.csv") as f:
        st.sidebar.download_button('See the example of biological data', f, file_name='biological.csv')

    chem = st.sidebar.file_uploader("Chemical Data")
    with open("data/data_chemical_v2.csv") as f:
        st.sidebar.download_button('See the example of chemical data', f, file_name='chemical.csv')


    st.sidebar.markdown("## Temperature")
    temp_suitable_min = st.sidebar.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = st.sidebar.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    
    temp_optimal_min = st.sidebar.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = st.sidebar.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    temp_upper_limit = st.sidebar.number_input("Temperature upper limit", value=36.0, step=1.,format="%.2f")
    temp_weight = st.sidebar.number_input("weight of temperature", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## Dissolved Oxygen")
    do_suitable_min = st.sidebar.number_input("DO suitable min", value=4.0, step=1.,format="%.2f") 
    do_suitable_max = st.sidebar.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    
    do_optimal_min = st.sidebar.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    do_optimal_max = st.sidebar.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    do_upper_limit = st.sidebar.number_input("DO upper limit", value=10.0, step=1.,format="%.2f") 
    do_weight = st.sidebar.number_input("weight of DO", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## Unionized Ammonia")
    ua_suitable_min = st.sidebar.number_input("UA suitable min", value=0.0, step=1.,format="%.2f") 
    ua_suitable_max = st.sidebar.number_input("UA suitable max", value=0.16, step=1.,format="%.2f") 
    
    ua_optimal_min = st.sidebar.number_input("UA optimal min", value=0.0001, step=1.,format="%.2f") 
    ua_optimal_max = st.sidebar.number_input("UA optimal max", value=0.06, step=1.,format="%.2f")

    ua_upper_limit = st.sidebar.number_input("UA upper limit", value=1.0, step=1.,format="%.2f") 
    ua_weight = st.sidebar.number_input("weight of UA", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## Critical Steady Crop (CSC)")
    csc_suitable_min = st.sidebar.number_input("CSC suitable min", value=0.0, step=1.,format="%.2f") 
    csc_suitable_max = st.sidebar.number_input("CSC suitable max", value=0.5, step=1.,format="%.2f") 
    
    csc_optimal_min = st.sidebar.number_input("CSC optimal min", value=0.0, step=1.,format="%.2f") 
    csc_optimal_max = st.sidebar.number_input("CSC optimal max", value=3.0, step=1.,format="%.2f")

    csc_upper_limit = st.sidebar.number_input("CSC upper limit", value=7.0, step=1.,format="%.2f") 
    csc_weight = st.sidebar.number_input("weight of CSC", value=1.0, step=1.,format="%.2f")  

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

    submit = st.sidebar.button("submit")

    if submit:
        if (bio is not None) & (chem is not None):

            bio_df = pd.read_csv(bio)
            bio_df.fillna(np.nan, inplace=True)
            # st.write(bio_df)

            # st.write("Chemical Data")
            chem_df = pd.read_csv(chem)
            chem_df.replace("-", np.nan, inplace=True)
            bio_df.fillna(np.nan, inplace=True)

            data_biomassa = []
            data_alpha = []
            data_wt = []
            data_population = []

            m = -np.log(sr)/T
            for i in range(T):
                if i == 0:
                    obj = Biomassa(t0, i, wn, w0, alpha, n0, sr, m, [partial1, partial2, partial3], [docpartial1, docpartial2, docpartial3], )
                    obj = PartialHarvest(t0, i, wn, w0, alpha, n0, sr, m, [partial1, partial2, partial3], [docpartial1, docpartial2, docpartial3], docfinal)
                else:
                    obj = PartialHarvest(t0, i, wn, w0, data_alpha[-1], n0, sr, m, [partial1, partial2, partial3], [docpartial1, docpartial2, docpartial3], docfinal)
                
                data_biomassa.append(obj.biomassa()/1000 * area)
                data_wt.append(obj.wt())
                data_population.append(obj.population())
                # print(i)å
                data_alpha.append(
                    alpha *
                    GrowthFunction(
                        bio_df[bio_df["DOC"] == i]["Suhu_s"].values[0], temp_suitable_min, temp_suitable_max, temp_optimal_min, temp_optimal_max, temp_upper_limit, 
                        bio_df[bio_df["DOC"] == i]["DO_s"].values[0], do_suitable_min, do_suitable_max, do_optimal_min, do_optimal_max, do_upper_limit, 
                        chem_df[chem_df["Doc"] == i]["uia"].values[0], ua_suitable_min, ua_suitable_max, ua_optimal_min, ua_optimal_max, ua_upper_limit,
                        data_biomassa[-1], area, csc_suitable_min, csc_suitable_max, csc_optimal_min, csc_optimal_max, csc_upper_limit
                    ).get_result()
                )


            option = Line("weight", list(range(T+1)), [data_wt], ["W(t)"], True).plot()
            st_echarts(options=option)

            option1 = Line("alpha", list(range(T+1)), [data_alpha], ["alpha"], True).plot()
            st_echarts(options=option1)

            option2 = Line("biomass", list(range(T+1)), [data_biomassa], ["biomass"], True).plot()
            st_echarts(options=option2)

        else:
            st.warning("Error. Maybe the system is error or you didn't upload data yet")