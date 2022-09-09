import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation_v3 import ParemeterEstimation
from lib.helpers import get_temperature_data, air_to_pond_temperature
from lib.plot import Line
import numpy as np
import pandas as pd
import timeit
from lib.population import population_v3, harvested_population, harvested_biomass, pond_remaining_biomass
from lib.helpers import heaviside_step

from scipy.interpolate import CubicSpline

def base_section():
    
    st.set_page_config(layout="wide")

    st.title("Unit Economic Model")
    st.markdown("Individual growth of shrimp in a cycle of cultivation. The perpose of this dashboard is to show the unit economic model which contains population, biomass, and the revenue model.")

    with open("data/sample_single_cycle.csv") as f:
        st.download_button('See the example of current growth shrimp data', f, file_name='growth.csv')

    form1 = st.form("Upload data for current cultivation")
    with form1:
        col1, col2 = st.columns(2)

        # col2.text("Parameter")
        # t0 = col2.number_input("t0", value=0)
    
        # T = col2.number_input("T", value=120)
        # wn = col2.number_input("wn", value=45)

        df = col1.file_uploader("Actual Growth Shrimp Data")
        separator = col1.text_input("seperator data in the csv table", value=",")

        condition_alpha = col1.checkbox("Use alpha from estimation parameter to forcast", value=False)
        if condition_alpha:
            report = pd.read_csv("data/alpha.csv")
            alpha = report.loc[0]
        else:
            alpha = col1.text_input("alpha (use comma to separate your value)", placeholder="example: 0.001, 1, 1, 1")
            alpha = alpha.replace(" ", "").split(",")
            try:
                alpha = list(map(lambda x: float(x) if not x.isalpha() else x, alpha))
            except:
                alpha = ""

        # col2.text("Parameter")
        final_doc = col2.number_input("Final DOC", value=105)

        ph = col2.text_input("partial harvest (use comma to separate your value)", value="10, 10, 10")
        ph = ph.replace(" ", "").split(",")
        ph = [int(i) for i in ph]

        doc = col2.text_input("doc (use comma to separate your value)", value="60, 80, 100")
        doc = doc.replace(" ", "").split(",")
        doc = [int(i) for i in doc]

        gamma = col2.number_input("Gamma", value=0.02)
        nh3_lim = col2.number_input("NH3 Limit", value=2.78)

        # st.markdown(""" `Please make sure that T is greater than` $t_0$ and your range of prediction not more than two weeks. In this case, $t_0$ and $w_{t_0}$ are obtained from the actual data. 
        #     $t_0$ is the last DOC and whereas $w_{t_0}$ is the last ABW which related to $t0$.
        # """)

        temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max = 25, 28, 32, 33
        uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max = 0, 0.0, 0.01, 0.02
        do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max = 4, 6, 9, 10

        plotting = st.form_submit_button("Plot")

    if plotting:

        try:
            ndf = pd.read_csv(df, sep=separator)
        except:
            ndf = pd.read_csv("data/data_test_01.csv")


        t0 = 0
        w0 = 0.05
        wn = 45
        n0 = 100
        sr = 0.92

        T = int(ndf["DOC"].max())+1

        m = -np.log(sr)/T

        model_test = ParemeterEstimation(df=ndf, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
        model_test.set_conditional_parameter(cond_temp=(
                                                temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max
                                            ), cond_uia=(
                                                uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max
                                            ), cond_do=(
                                                do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max
                                            ), cond_csc=(
                                                0, 0, 0, 0
                                            ))
        model_test.set_temperature_interpolation()
        model_test.set_food_availablelity_data()
        model_test.set_growth_paremater(t0=t0, w0=w0, wn=wn, n0=n0, sr=sr)
        model_test.set_interpolate_biochem(ndf)

        weight = model_test.multiple_operation_v2(ndf["DOC"], alpha[0], alpha[1], alpha[2], alpha[3])

        option_wt = Line("weight", list(range(T)), [weight], labels=["weight"]).plot()
        st_echarts(options=option_wt)

        pops = []
        for i in range(T):
            pops.append(
                population_v3(i, n0, m, ph, doc, gamma, model_test.f_nh4, nh3_lim)
            )

        pops = np.array(pops)

        sec_1_col1, sec_1_col2 = st.columns(2)

        with sec_1_col1:
            option_pops = Line("Population", list(range(T)), [pops.tolist()], labels=["population"]).plot()
            st_echarts(options=option_pops)

        biomass = weight * pops / 1000

        with sec_1_col2:
            option_bio = Line("Biomass", list(range(T)), [biomass.tolist()], labels=["Biomassa (kg)"]).plot()
            st_echarts(options=option_bio)

        

        harvest_pops = []
        for i in range(T):
            harvest_pops.append(
                harvested_population(i, n0, m, ph, doc, final_doc, gamma, model_test.f_nh4, nh3_lim)
            )

        
        option_harvest_pop = Line("Harvested Population", list(range(T)), [harvest_pops], labels=["harvested population"]).plot()
        st_echarts(options=option_harvest_pop)

        price = pd.read_csv("data/shrimp_price.csv")
        price = price.melt(id_vars=["date"], value_vars=['size_20', 'size_30', 'size_40', 'size_50',
            'size_60', 'size_70', 'size_80', 'size_90', 'size_100', 'size_110',
            'size_120', 'size_130', 'size_140', 'size_150', 'size_160', 'size_170',
            'size_180', 'size_190', 'size_200'], var_name="size", value_name="price"
        )

        price["size"] = price["size"].apply(lambda x: int(x.split("_")[1]))

        rbio = []
        for i in range(T):
            rbio.append(
                pond_remaining_biomass(i, weight[i], n0, m, ph, doc, gamma, model_test.f_nh4, nh3_lim)
            )
        
        hbio = []
        for i in range(T):
            hbio.append(
                harvested_biomass(i, weight[i], n0, m, ph, doc, final_doc, gamma, model_test.f_nh4, nh3_lim)
            )

        
        data_to_interpolate = price.groupby("size").mean()
        f = CubicSpline([0] + data_to_interpolate.index.tolist(), [0] + data_to_interpolate["price"].tolist())

        realized_revenue = []

        for i, j in enumerate(weight):
            realized_revenue.append(hbio[i] * f(1000/j))

        realized_revenue = np.cumsum(realized_revenue)

        potential_revenue = []

        for i, j in enumerate(weight):
            price = f(1000/j)
            tetha = heaviside_step(price)
            potential_revenue.append((rbio[i] * tetha * price))


        option_revenuw = Line("Revenue", list(range(T)), [potential_revenue, realized_revenue.tolist()], labels=["potential", "realized"], legend=True).plot()
        st_echarts(options=option_revenuw)        





            