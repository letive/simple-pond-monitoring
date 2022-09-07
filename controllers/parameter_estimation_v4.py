from weakref import CallableProxyType
import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation_v3 import ParemeterEstimation
from lib.helpers_mod.helpers import get_cycle_range
from lib.plot import LineScatter, Scatter
import numpy as np
import pandas as pd
import timeit

def base_section():
    
    st.set_page_config(layout="wide")
    
    t0 = st.sidebar.number_input("t0", value=0)
    # sr = st.sidebar.number_input("survival rate", value=0.92)
    # n0 = st.sidebar.number_input("n0", value=100)
    T = st.sidebar.number_input("T", value=120)    
    # area = st.sidebar.number_input("area", value=1000)
    # alpha = st.sidebar.number_input("alpha (shrimp growth rate)", value=1.0, step=1.,format="%.2f")/100 

    w0 = st.sidebar.number_input("w0", value=0.05)
    wn = st.sidebar.number_input("wn", value=45)

    # partial1 = st.sidebar.number_input("partial1", value=0.1)
    # partial2 = st.sidebar.number_input("partial2", value=0.1)
    # partial3 = st.sidebar.number_input("partial3", value=0.1)
    
    # docpartial1 = int(st.sidebar.number_input("doc partial 1", value=60))
    # docpartial2 = int(st.sidebar.number_input("doc partial 2", value=70))
    # docpartial3 = int(st.sidebar.number_input("doc partial 3", value=80))
    # docfinal = int(st.sidebar.number_input("doc final", value=120))

    st.sidebar.markdown(""" 
        ## Upload Data 

        Upload multi cycle data for more options to show and make sure the inital DOC equal to 1.
    
    """)

    df = st.sidebar.file_uploader("Growth Shrimp Data")
    separator = st.sidebar.text_input("seperator data in the csv table", value=",")
    with open("data/sample_data_multicycle.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')

    st.sidebar.markdown("## Criterion")
    temp_condition = st.sidebar.expander("Temperature condition")
    temp_suitable_min = temp_condition.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = temp_condition.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    temp_optimal_min = temp_condition.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = temp_condition.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    uia_condition = st.sidebar.expander("Unionized Amonia condition")
    uia_suitable_min = uia_condition.number_input("NH4 suitable min", value=0.0, step=1.,format="%.2f") 
    uia_suitable_max = uia_condition.number_input("NH4 suitable max", value=0.02, step=1.,format="%.2f") 
    uia_optimal_min = uia_condition.number_input("NH4 optimal min", value=0.0, step=1.,format="%.2f") 
    uia_optimal_max = uia_condition.number_input("NH4 optimal max", value=0.01, step=1.,format="%.2f")

    do_conditon = st.sidebar.expander("Dissolved Oxygen Condition")
    do_suitable_min = do_conditon.number_input("DO suitable min", value=5.0, step=1.,format="%.2f") 
    do_suitable_max = do_conditon.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    do_optimal_min = do_conditon.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    do_optimal_max = do_conditon.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    # csc_conditon = st.sidebar.expander("Critical Steady Crop Condition")
    # csc_suitable_min = csc_conditon.number_input("CSC suitable min", value=0.0, step=1.,format="%.2f") 
    # csc_suitable_max = csc_conditon.number_input("CSC suitable max", value=3.0, step=1.,format="%.2f") 
    # csc_optimal_min = csc_conditon.number_input("CSC optimal min", value=0.0, step=1.,format="%.2f") 
    # csc_optimal_max = csc_conditon.number_input("CSC optimal max", value=0.5, step=1.,format="%.2f")

    csc_suitable_min, csc_optimal_min, csc_optimal_max, csc_suitable_max = 0, 0, 0, 0
    

    submit = st.sidebar.button("submit")

    if submit:
        try:
            root_df = pd.read_csv(df, sep=separator)
        except:
            root_df = pd.read_csv("data/data_test_01.csv")
        cycle = get_cycle_range(root_df)
        alpha1 = []
        alpha2 = []
        alpha3 = []
        alpha4 = []
        time_expense = []
        error = []

        for i in cycle:
            if len(i) == 2:
                df = root_df.loc[i[0]:i[1]-1]
            else:
                df = root_df.loc[i[0]:]


            start_time = timeit.default_timer()

            model = ParemeterEstimation(df=df, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
            model.set_conditional_parameter(cond_temp=(
                                                    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                                ), cond_uia=(
                                                    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                                ), cond_do=(
                                                    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                                ), cond_csc=(
                                                    csc_suitable_min, csc_optimal_min, csc_optimal_max, csc_suitable_max
                                                ))
            model.set_temperature_interpolation()
            model.set_food_availablelity_data()
            model.set_growth_paremater(t0=t0, w0=w0, wn=wn, n0=0, sr=0.92)
            model.set_interpolate_biochem(df)
            # model.set_partial_harvest_parameter(doc=[docpartial1, docpartial2, docpartial3], ph=[partial1, partial2, partial3], final_doc=docfinal)
            # model.set_pond_data(area=area)

            alpha = model.fit()

            end_time = timeit.default_timer()
            
            alpha1.append(alpha[0])
            alpha2.append(alpha[1])
            alpha3.append(alpha[2])
            alpha4.append(alpha[3])

            time_expense.append(end_time - start_time)
            error.append(model.mse())

        report = pd.DataFrame({
            "alpha1": alpha1,
            "alpha2": alpha2,
            "alpha3": alpha3,
            "alpha4": alpha4,
            "error": error,
            "time_expense": time_expense
        })

        report.to_csv("data/alpha.csv", index=False)

        st.markdown("""
            # Summary

            This is a summary of the estimation parameter for cyle/cycles of shrimp growth model. Table below shows the alpha or the paramters of our shrimp growth model, 
            time of estimation, and error of the estimation. 
        """)
        st.write(report)

        st.markdown("""
            The next section is a visualization for comparison of realized vs simulated the shrimp growth data. In each cycle there will be visualization for temperature, $NH_3$ and dissolved oxygen.
            Besides that, there is also a table which is shrimp growth data that is used to create estimation.
        """)
                
        for j, i in enumerate(cycle):
            if len(i) == 2:
                ndf = root_df.loc[i[0]:i[1]-1]
            else:
                ndf = root_df.loc[i[0]:]

            st.markdown("## Cycle - {}".format(j+1))
            st.markdown("---")

            model_test = ParemeterEstimation(df=ndf, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
            model_test.set_conditional_parameter(cond_temp=(
                                                    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                                ), cond_uia=(
                                                    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                                ), cond_do=(
                                                    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                                ), cond_csc=(
                                                    csc_suitable_min, csc_optimal_min, csc_optimal_max, csc_suitable_max
                                                ))
            model_test.set_temperature_interpolation()
            model_test.set_food_availablelity_data()
            model_test.set_growth_paremater(t0=t0, w0=w0, wn=wn, n0=100, sr=0.92)
            model_test.set_interpolate_biochem(ndf)
            # model_test.set_partial_harvest_parameter(doc=[docpartial1, docpartial2, docpartial3], ph=[partial1, partial2, partial3], final_doc=docfinal)
            # model_test.set_pond_data(area=area)
            
            a1, a2, a3, a4 = tuple(report[["alpha1", "alpha2", "alpha3", "alpha4"]].iloc[j].values)
            weight = model_test.multiple_operation_v2(ndf["DOC"], a1, a2, a3, a4)

            col1, col2 = st.columns((3, 1))

            with col1:
                option2 = LineScatter("Weight (Gr)", ndf["DOC"].tolist(), weight, ndf["DOC"].tolist(), ndf["ABW"].tolist(), labels=["estimation", "abw"]).plot()
                st_echarts(options=option2)

                ndf.replace(np.nan, None, inplace=True)

                option3 = Scatter("Temperature",  ndf["DOC"].tolist(), ndf["Temp"].tolist()).plot()
                st_echarts(options=option3)

                option4 = Scatter("DO",  ndf["DOC"].tolist(), ndf["DO"].tolist()).plot()
                st_echarts(options=option4)

                option5 = Scatter("NH3", ndf["DOC"].tolist(), ndf["NH3"].tolist()).plot()
                st_echarts(options=option5)

            col2.markdown("### data source")
            col2.dataframe(ndf)
            