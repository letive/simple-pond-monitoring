import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation import ParemeterEstimation

from lib.plot import Line, LineScatter
import pandas as pd
import numpy as np
import math

def base_section():
    
    st.set_page_config(layout="wide")
    
    t0 = st.sidebar.number_input("t0", value=0)
    sr = st.sidebar.number_input("survival rate", value=0.92)
    n0 = st.sidebar.number_input("n0", value=100)
    T = st.sidebar.number_input("T", value=120)
        
    area = st.sidebar.number_input("area", value=1000)
    # alpha = st.sidebar.number_input("alpha (shrimp growth rate)", value=1.0, step=1.,format="%.2f")/100 

    w0 = st.sidebar.number_input("w0", value=0.05)
    wn = st.sidebar.number_input("wn", value=45)

    partial1 = st.sidebar.number_input("partial1", value=0.1)
    partial2 = st.sidebar.number_input("partial2", value=0.1)
    partial3 = st.sidebar.number_input("partial3", value=0.1)
    
    docpartial1 = int(st.sidebar.number_input("doc partial 1", value=60))
    docpartial2 = int(st.sidebar.number_input("doc partial 2", value=70))
    docpartial3 = int(st.sidebar.number_input("doc partial 3", value=80))
    docfinal = int(st.sidebar.number_input("doc final", value=120))

    

    st.sidebar.markdown("## Upload Data")
    df = st.sidebar.file_uploader("Growth Shrimp Data")
    with open("data/growth_full2.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')


    temp_condition = st.sidebar.expander("Temperature condition")
    temp_suitable_min = temp_condition.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = temp_condition.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    temp_optimal_min = temp_condition.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = temp_condition.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    uia_condition = st.sidebar.expander("Unionized Amonia condition")
    uia_suitable_min = uia_condition.number_input("NH4 suitable min", value=0.0, step=1.,format="%.2f") 
    uia_suitable_max = uia_condition.number_input("NH4 suitable max", value=25, step=1.,format="%.2f") 
    uia_optimal_min = uia_condition.number_input("NH4 optimal min", value=0.001, step=1.,format="%.2f") 
    uia_optimal_max = uia_condition.number_input("NH4 optimal max", value=18, step=1.,format="%.2f")

    do_conditon = st.sidebar.expander("Dissolved Oxygen Condition")
    do_suitable_min = do_conditon.number_input("DO suitable min", value=4.0, step=1.,format="%.2f") 
    do_suitable_max = do_conditon.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    do_optimal_min = do_conditon.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    do_optimal_max = do_conditon.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    csc_conditon = st.sidebar.expander("Critical Steady Crop Condition")
    csc_suitable_min = csc_conditon.number_input("CSC suitable min", value=0.0, step=1.,format="%.2f") 
    csc_suitable_max = csc_conditon.number_input("CSC suitable max", value=3.0, step=1.,format="%.2f") 
    csc_optimal_min = csc_conditon.number_input("CSC optimal min", value=0.0, step=1.,format="%.2f") 
    csc_optimal_max = csc_conditon.number_input("CSC optimal max", value=0.5, step=1.,format="%.2f")

    # e = st.sidebar.number_input("energy day cost", value=4.0, step=1.,format="%.2f")
    # p = st.sidebar.number_input("daily probiotics", value=120000)
    # o = st.sidebar.number_input("others cost", value=30000)
    # labor = st.sidebar.number_input("labor cost", value=2000000)/30
    # bonus = st.sidebar.number_input("bonus", value=2000)
    # h = st.sidebar.number_input("harvest cost per kg", value=1000)
    # r = st.sidebar.number_input("feeding rate", value=0.04)
    # fc = st.sidebar.number_input("feeding price", value=16000)
    # formula = st.sidebar.selectbox("formula", (1, 2))

    submit = st.sidebar.button("submit")

    if submit:

        # from lib.v2.parameter_estimation import ParemeterEstimation
        try:
            estimator = ParemeterEstimation(df=df, sep=";", col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")
        except:
            estimator = ParemeterEstimation(path = "data/growth_full2.csv", sep=";", col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")

        # intial setup
        estimator.set_data_for_interpolation(path = "data/biochem.csv")
        estimator.set_conditional_parameter(cond_temp=(
                                                temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                            ), cond_uia=(
                                                uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                            ), cond_do=(
                                                do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                            ), cond_csc=(
                                                csc_suitable_min, csc_optimal_min, csc_optimal_max, csc_suitable_max
                                            ))
        estimator.set_food_availablelity_data()
        estimator.set_growth_paremater(w0=w0, wn=wn, n0=n0, sr=sr)
        estimator.set_partial_harvest_parameter(doc=[docpartial1, docpartial2, docpartial3], ph=[partial1, partial2, partial3], final_doc=docfinal)
        estimator.set_pond_data(area=area)

        alpha, alpha2, alpha3, alpha4, alpha5, alpha6 = estimator.fit()


        df = estimator.df.copy()
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## Parameter")
            st.latex(
                r"""
                \alpha = {}
                """.format(alpha)
            )

            st.latex(
                r"""\alpha_2 = {}""".format(alpha2)
            )

            st.latex(
                r"""\alpha_3 = {}""".format(alpha3)
            )
            st.latex(
                r"""\alpha_4 = {}""".format(alpha4)
            )
            st.latex(
                r"""\alpha_5 = {}""".format(alpha5)
            )
            st.latex(
                r"""\alpha_6 ={}""".format(alpha6)
            )
        
        with col2:
            st.dataframe(df)

        m = -np.log(sr)/T

        weight = []
        bio = []
        index = list(range(T+1))
        abw = []
        temp = []
        do = []
        nh4 = []
        csc = []
        fa = []

        for t in index:

            wt, biomass = estimator.single_operation(0, t, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6)
           
            csc.append(estimator.csc/alpha5)
            fa.append(estimator.fa)

            weight.append(wt)
            bio.append(biomass)
            try:
                abw.append(float(df[df["DOC"]== t]["ABW"].values[0]))
                temporary_temp = float(df[df["DOC"]== t]["Temp"].values[0])
                temporary_do = float(df[df["DOC"]== t]["DO"].values[0])
                temporary_nh4 = float(df[df["DOC"]== t]["NH4"].values[0])

                if math.isnan(temporary_temp):
                    temp.append(None)
                else:
                    temp.append(temporary_temp)

                if math.isnan(temporary_do):
                    do.append(None)
                else:
                    do.append(temporary_do)
                
                if math.isnan(temporary_nh4):
                    nh4.append(None)
                else:
                    nh4.append(temporary_nh4)
            except:
                abw.append(None)
                temp.append(None)
                do.append(None)
                nh4.append(None)
    
        option2 = LineScatter("Weight (Gr)", index, weight, index, abw, labels=["estimation", "abw"]).plot()

        st_echarts(options=option2)

        option3 = Line("Temperature", index, y=[temp], labels=["Temperature"]).plot()
        st_echarts(options=option3)

        option4 = Line("Unionized Amonia", index, y=[nh4], labels=["NH4"]).plot()
        st_echarts(options=option4)

        option5 = Line("Dissolved Oxygen", index, y=[do], labels=["DO"]).plot()
        st_echarts(options=option5)

        option6 = Line("Critical Steady Crop", index, y=[csc], labels=["CSC"]).plot()
        st_echarts(options=option6)

        option7 = Line("Food Availablelity", index, y=[fa], labels=["Food Availablelity"]).plot()
        st_echarts(options=option7)

        st.markdown(""" 
        
        ### Food Availablelity Parameter Data

        Data ini digunakan untuk pembanding berdasarkan weight dan temperature. Saat ini apabila data belum memenuhi kondisi temperature dan weight maka food availablelity-nya sama dengan 0.
        """)
        

        st.write(estimator.fa_data)
            