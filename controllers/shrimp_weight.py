import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation_v4 import ParemeterEstimation
from lib.helpers import get_temperature_data, air_to_pond_temperature
from lib.plot import LineForecast
import numpy as np
import pandas as pd

def set_checkbox():
    st.session_state['alpha'] = True

def base_section():

    st.title("Shrimp Weight")
    st.markdown("Individual growth of shrimp in a cycle of cultivation. The purpose of this dashboard is to show the forecast of growth shrimp. Before you start to use it, we suggest you download our data standard to use in this function. ")

    with open("data/sample_single_cycle.csv") as f:
        st.download_button('See the example of growth shrimp data', f, file_name='growth.csv')

    # form1 = st.form("Upload Data")
    # with form1:
    col1, col2 = st.columns(2)

    # col2.text("Parameter")
    # t0 = col2.number_input("t0", value=0)

    T = col2.number_input("T", value=120)
    # wn = col2.number_input("wn", value=45)

    df = col1.file_uploader("Actual Growth Shrimp Data")
    separator = col1.text_input("seperator data in the csv table", value=",")

    # condition_alpha = col2.checkbox("Use alpha from estimation parameter to forcast", value=True)
    # if condition_alpha:
    #     report = pd.read_csv("data/alpha.csv")
    #     alpha = report.loc[0]
    # else:
    #     alpha = col2.text_input("alpha (use comma to separate your value)", placeholder="example: 0.001, 1, 1, 1")
    #     alpha = alpha.replace(" ", "").split(",")
    #     try:
    #         alpha = list(map(lambda x: float(x) if not x.isalpha() else x, alpha))
    #     except:
    #         alpha = ""

    col2.markdown(""" `Please make sure that T is greater than` $t_0$ and your range of prediction not more than two weeks. In this case, $t_0$ and $w_{t_0}$ are obtained from the actual data. 
        $t_0$ is the last DOC and whereas $w_{t_0}$ is the last ABW which related to $t0$.
    """)

    # col3.text("Set Condition")
    # temp_condition = col3.expander("Temperature condition")
    # temp_suitable_min = temp_condition.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    # temp_suitable_max = temp_condition.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    # temp_optimal_min = temp_condition.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    # temp_optimal_max = temp_condition.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    # uia_condition = col3.expander("Unionized Amonia condition")
    # uia_suitable_min = uia_condition.number_input("NH4 suitable min", value=0.0, step=1.,format="%.2f") 
    # uia_suitable_max = uia_condition.number_input("NH4 suitable max", value=0.02, step=1.,format="%.2f") 
    # uia_optimal_min = uia_condition.number_input("NH4 optimal min", value=0.0, step=1.,format="%.2f") 
    # uia_optimal_max = uia_condition.number_input("NH4 optimal max", value=0.01, step=1.,format="%.2f")

    # do_conditon = col3.expander("Dissolved Oxygen Condition")
    # do_suitable_min = do_conditon.number_input("DO suitable min", value=4.0, step=1.,format="%.2f") 
    # do_suitable_max = do_conditon.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    # do_optimal_min = do_conditon.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    # do_optimal_max = do_conditon.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max = 25, 28, 32, 33
    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max = 0, 0.0, 0.01, 0.02
    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max = 4, 6, 9, 10

    wn = 45

        # plotting = st.form_submit_button("Plot")
    plotting = st.button("Plot")

    st.markdown("---")

    if plotting:

        try:
            ndf = pd.read_csv(df, sep=separator)
        except:
            ndf = pd.read_csv("data/data_test_01.csv")

        t0 = int(ndf["DOC"].max())
        w0 = ndf["ABW"].max()

        if (t0 <= T) and ((T-t0) <= 15) :
            doc = list(range(t0, T))

            ndf.replace(np.nan, None, inplace=True)

            previous_temp = ndf["Temp"].max()
            temp_data = get_temperature_data()
            temp_data = air_to_pond_temperature(temp_data, previous_temp)

            doc = list(range(t0, T))

            bio_chem = pd.DataFrame({
                "DOC": doc,
                "Temp": temp_data["pond_temp"].loc[:len(doc)-1],
                "DO": [ndf["DO"].mean()]*len(doc),
                "NH3": [ndf["NH3"].mean()]*len(doc),
                "ABW": [0]*len(doc)
            })

            model = ParemeterEstimation(df=ndf, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
            model.set_conditional_parameter(cond_temp=(
                                                    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                                ), cond_uia=(
                                                    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                                ), cond_do=(
                                                    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                                ))
            model.set_temperature_interpolation()
            model.set_growth_paremater(t0=0, w0=0.05, wn=wn)
            model.set_interpolate_biochem()

            origin_doc = model.df["DOC"].tolist() + doc[1:]
            alpha = model.fit()


            model_test = ParemeterEstimation(df=bio_chem, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
            model_test.set_conditional_parameter(cond_temp=(
                                                    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                                ), cond_uia=(
                                                    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                                ), cond_do=(
                                                    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                                ))
            model_test.set_temperature_interpolation()
            model_test.set_growth_paremater(t0=t0, w0=w0, wn=wn)
            model_test.set_interpolate_biochem()

            weight = model_test.weight(doc, alpha[0], alpha[1], alpha[2], alpha[3])

            st.write(model.df)

            option = LineForecast("Shrimp Growth Forecast", origin_doc, 
                [model.df["ABW"].tolist() + weight[1:] ], len(model.df["DOC"].tolist()), labels=["value"],
            base_color="#3AAE8E",forecast_color="#fb0166" ).plot()
            option["xAxis"]["name"] = "DOC"
            option["yAxis"]["name"] = "ABW (gr)"
            option["yAxis"]["nameLocation"] = "middle"
            option["yAxis"]["nameGap"] = 50
            option["series"][0]["smooth"] = True
            st_echarts(options=option)

            st.code(str(option), language="json")
        else:
            st.error("Error. Maybe your T not in range or your range of prediction more than 2 weeks")