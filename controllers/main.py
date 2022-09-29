import streamlit as st
from streamlit_echarts import st_echarts
from lib.v2.parameter_estimation_v4 import ParemeterEstimation
from lib.helpers_mod.helpers import get_cycle_range
from lib.plot import LineScatter, Scatter, Bar, Line, Pie
import numpy as np
import pandas as pd
import timeit
from lib.population import population_v3, harvested_population, harvested_biomass, pond_remaining_biomass
from lib.helpers import heaviside_step, feeding_expense

from scipy.interpolate import CubicSpline


def base_section():
    t0, T, w0, wn = 0, 120, 0.05, 45

    st.sidebar.markdown("""### Upload Data """)

    df = st.sidebar.file_uploader("Shrimp Growth Data")
    separator = st.sidebar.text_input("seperator data in the csv table", value=",")
    with open("data/sample_data_multicycle.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')

    temp_suitable_min, temp_optimal_min, temp_optimal_max, temp_suitable_max = 25, 28, 32, 33
    uia_suitable_min, uia_optimal_min, uia_optimal_max, uia_suitable_max = 0, 0, 0.01, 0.02
    do_suitable_min, do_optimal_min, do_optimal_max, do_suitable_max = 4, 6, 9, 10

    cost_expander = st.sidebar.expander("Cost Parameters")
    
    e = cost_expander.number_input("energy day cost", value=4.0, step=1.,format="%.2f")
    p = cost_expander.number_input("daily probiotics", value=120000)
    o = cost_expander.number_input("others cost", value=30000)
    labor = cost_expander.number_input("labor cost", value=2000000)/30
    bonus = cost_expander.number_input("bonus", value=2000)
    h = cost_expander.number_input("harvest cost per kg", value=1000)
    r = cost_expander.number_input("feeding rate", value=0.04)
    fc = cost_expander.number_input("feeding price", value=16000)
    formula = cost_expander.selectbox("formula", (1, 2))

    pop_expander = st.sidebar.expander("Population Parameter")
    n0 = pop_expander.number_input("N0", value=1000)
    area = pop_expander.number_input("Area", value=1000)

    ph = pop_expander.text_input("Total partial harvest (use comma to separate your value)", value="10, 10, 10")
    ph = ph.replace(" ", "").split(",")
    ph = [int(i) for i in ph]

    doc = pop_expander.text_input("DOC of partial harvest (use comma to separate your value)", value="60, 80, 100")
    doc = doc.replace(" ", "").split(",")
    doc = [int(i) for i in doc]

    final_doc = pop_expander.number_input("Final DOC", value=105)

    gamma = pop_expander.number_input("Gamma", value=0.02)
    sr = pop_expander.number_input("Survival Rate", value=0.92)
    nh3_lim = pop_expander.number_input("NH3 Limit", value=2.78)

    # cost_energy = 4
    # cost_probiotics = 120000
    # cost_others = 30000
    # cost_labor = 2000000/30
    # cost_bonus = 2000
    # cost_harvest = 1000
    # feeding_rate = 0.04
    # feeding_price = 16000
    # count_formula = 1

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
                                                ))
            model.set_temperature_interpolation()
            model.set_growth_paremater(t0=t0, w0=w0, wn=wn)
            model.set_interpolate_biochem()
    
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


        model_test = ParemeterEstimation(df=df, col_temp="Temp", col_uia="NH3", col_do="DO", col_doc="DOC")
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
        
        a1, a2, a3, a4 = tuple(report[["alpha1", "alpha2", "alpha3", "alpha4"]].iloc[0].values)
        weight = model_test.weight(model.df["DOC"], a1, a2, a3, a4)


        ##### Population
        T = df["DOC"].max()
        m = -np.log(sr)/T

        pops = []
        for i in range(T):
            pops.append(
                population_v3(i, n0, m, ph, doc, gamma, model_test.f_nh4, nh3_lim)
            )

        pops = np.array(pops)

        sec_1_col1, sec_1_col2 = st.columns(2)

        with sec_1_col1:
            option_pops = Bar("Population", list(range(T)), [pops.tolist()], labels=["population"]).plot()
            option_pops["color"] = ["#3AAE8E", "#fb0166"]
            # st_echarts(options=option_pops)

        biomass = weight * pops / 1000

        with sec_1_col2:
            option_bio = Line("Biomass", list(range(T)), [biomass.tolist()], labels=["Biomassa (kg)"]).plot()
            option_bio["color"] = ["#3AAE8E", "#fb0166"]
            # st_echarts(options=option_bio)

        harvest_pops = []
        for i in range(T):
            harvest_pops.append(
                harvested_population(i, n0, m, ph, doc, final_doc, gamma, model_test.f_nh4, nh3_lim)
            )

        harvest_pops = np.cumsum(harvest_pops).tolist()        

        option_harvest_pop = Line("Harvested Population", list(range(T)), [harvest_pops], labels=["harvested population"]).plot()
        option_harvest_pop["color"] = ["#3AAE8E", "#fb0166"]
        # st_echarts(options=option_harvest_pop)

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


        ########
        # Cost Expense
        ########

        # harvested cost
        cost_harvest = np.array(hbio)*h

        # energy cost
        cost_energy = np.ones(T)*e*820*24

        # probiotics cost
        cost_probiotics = np.array([p if i < final_doc else 0 for i in range(T)])

        # other cost
        cost_other = np.array([o if i < final_doc else 0 for i in range(T)])

        # labor
        cost_labor = np.array([labor if i < final_doc else 0 for i in range(T)])

        # bonuss expense
        cost_bonuss = bonus * np.array(hbio)

        # feed cost
        cost_feed = np.array([feeding_expense(i, fc, biomass[i], final_doc, formula, r) for i in range(T)])

        all_data_cost = np.array([cost_harvest, cost_energy, cost_probiotics, cost_other, cost_labor, cost_bonuss, cost_feed])
        daily_cost = all_data_cost.sum(axis=0)

        profit = realized_revenue - daily_cost

        # option_revenue = Line("Revenue", list(range(T)), 
        #         [potential_revenue, realized_revenue.tolist(), profit.tolist()], 
        #         labels=["potential", "realized", "profit"], 
        #         legend=True).plot()

        option_revenue = Line("Revenue", list(range(T)), 
                [potential_revenue, realized_revenue.tolist()], 
                labels=["potential", "realized"], 
                legend=True).plot()

        option_revenue["color"] = ["#3AAE8E", "#fb0166", "#3963ff"]

        dataviz = [
            {
                "value": cost_harvest.sum(),
                "name": "Harvested"
            }, {
                "value": cost_energy.sum(),
                "name": "Energy Consumption"
            }, {
                "value": cost_probiotics.sum(),
                "name": "Probiotics"
            }, {
                "value": cost_other.sum(),
                "name": "Others"
            }, {
                "value": cost_labor.sum(),
                "name": "Labor"
            }, {
                "value": cost_bonuss.sum(),
                "name": "Bonus"
            }, {
                "value": cost_feed.sum(),
                "name": "Feed"
            }
        ]

        cost_option = Pie(title="Cost", data=dataviz, douhgnut=True, legend=True).plot()


        vis_col1, vis_col2 = st.columns((3,1))
        with vis_col1:
            st_echarts(options=option_revenue)
        
        with vis_col2:
            st_echarts(options=cost_option)
