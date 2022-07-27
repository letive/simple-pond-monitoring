import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation_without_csc_fa import ParemeterEstimation

from lib.plot import LineScatter, Scatter
import numpy as np
import pandas as pd

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
    separator = st.sidebar.text_input("seperator data in the csv table", value=";")
    with open("data/growth_full2.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')

    st.sidebar.markdown("## Criterion")
    temp_condition = st.sidebar.expander("Temperature condition")
    temp_suitable_min = temp_condition.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = temp_condition.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    temp_optimal_min = temp_condition.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = temp_condition.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    uia_condition = st.sidebar.expander("Unionized Amonia condition")
    uia_suitable_min = uia_condition.number_input("NH4 suitable min", value=0.0, step=1.,format="%.2f") 
    uia_suitable_max = uia_condition.number_input("NH4 suitable max", value=25.0, step=1.,format="%.2f") 
    uia_optimal_min = uia_condition.number_input("NH4 optimal min", value=0.001, step=1.,format="%.2f") 
    uia_optimal_max = uia_condition.number_input("NH4 optimal max", value=15.0, step=1.,format="%.2f")

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
        try:
            df = pd.read_csv(df, sep=separator)
            estimator = ParemeterEstimation(df=df, sep=separator, col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")
        except:
            estimator = ParemeterEstimation(path = "data/growth_002.csv", sep=",", col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")

        # initial setup
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
        alpha, alpha2, alpha3, alpha4 = estimator.fit_v2()

        df = estimator.df.copy()
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## Parameter")
            st.markdown(r"$\alpha = {}$".format(alpha))
            st.markdown(r"$\alpha_2 = {}$".format(alpha2))
            st.markdown(r"$\alpha_3 = {}$".format(alpha3))
            st.markdown(r"$\alpha_4 = {}$".format(alpha4))
            st.markdown(r"MSE = {}".format(estimator.mse()))
            # st.latex(
            #     r"""\alpha_5 = {}""".format(alpha5)
            # )
            # st.latex(
            #     r"""\alpha_6 ={}""".format(alpha6)
            # )
        
        with col2:
            st.dataframe(df)

        m = -np.log(sr)/T

        weight = []
        # bio = []
        index = list(range(T+1))
        # abw = []
        # temp = []
        # do = []
        # nh4 = []
        # csc = []
        # fa = []

        data = estimator.df.copy()
        data1 = estimator.df.copy()
        data1 = data1.loc[0:102]

        # modeling
        model = ParemeterEstimation(df=data1, col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")
        
        model.set_data_for_interpolation(path = "data/biochem.csv")
        model.set_conditional_parameter(cond_temp=(
                                                temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                            ), cond_uia=(
                                                uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                            ), cond_do=(
                                                do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                            ), cond_csc=(
                                                csc_suitable_min, csc_optimal_min, csc_optimal_max, csc_suitable_max
                                            ))
        model.set_food_availablelity_data()
        model.set_growth_paremater(w0=w0, wn=wn, n0=n0, sr=sr)
        model.set_partial_harvest_parameter(doc=[docpartial1, docpartial2, docpartial3], ph=[partial1, partial2, partial3], final_doc=docfinal)
        model.set_pond_data(area=area)

        for idx, row in data1.iterrows():
            wt, _ = model.single_operation_v2(0, row["DOC"], alpha, alpha2, alpha3, alpha4)
            weight.append(wt)

            # temp.append(estimator.temperature[0])
            # do.append(estimator.do[0])
            # nh4.append(estimator.nh4[0])

        
    
        option2 = LineScatter("Weight (Gr)", data1["DOC"].tolist(), weight, df["DOC"].tolist(), df["ABW"].tolist(), labels=["estimation", "abw"]).plot()
        option2["dataZoom"] = [{
            # "type":"inside",
            "start": 0, 
            "end": 30
        }]
        st_echarts(options=option2)


        data.replace(np.nan, None, inplace=True)

        option3 = Scatter("Temperature",  data["DOC"].tolist(), data["Temp"].tolist()).plot()
        st_echarts(options=option3)

        option4 = Scatter("DO",  data["DOC"].tolist(), data["DO"].tolist()).plot()
        st_echarts(options=option4)

        option5 = Scatter("NH4", data["DOC"].tolist(), data["NH4"].tolist()).plot()
        st_echarts(options=option5)

            