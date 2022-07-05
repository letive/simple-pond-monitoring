import streamlit as st
from streamlit_echarts import st_echarts
from lib.parameter_estimation import Estimate
from lib.biomass_after_estimate import single_wt
from lib.plot import Line, Pie
import pandas as pd
import numpy as np

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
        df = pd.read_csv("data/growth_full.csv", sep=",")
        alpha, alpha2, alpha3, alpha4, alpha5, alpha6 = Estimate(t0, w0, wn, n0, sr, 
                                                    [partial1, partial2, partial3], 
                                                    [docpartial1, docpartial2, docpartial3],
                                                    df["DOC"].tolist(), df["ABW"].tolist(), docfinal).fitting()


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
        
        m = -np.log(sr)/T

        weight = []
        bio = []
        index = list(range(T+1))
        for t in index:
            wt, biomass = single_wt(t, sr, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6, 
                t0=t0, wn=wn, w0=w0, n0=n0, ph=[partial1, partial2, partial3], 
                doc=[docpartial1, docpartial2, docpartial3], final_doc=docfinal)
           
            weight.append(wt)
            bio.append(biomass)

        option2 = Line("Weight", index, [weight], ["Weight (Gr)"]).plot()
        st_echarts(options=option2)
        

        # data = cost_structure(t0, T, area, wn, w0, alpha, n0, sr, [partial1, partial2, partial3], [docpartial1, docpartial2, docpartial3], e, p, o, labor, bonus, h, r, fc, formula, docfinal)
        # index = [t for t in range(t0, T+1)]

        # # option = Line("Individual weight in gr", index, [data["revenue"]["body_weight"]], ["Wt"]).plot()
        # # st_echarts(options=option)

        # partial4 = sr-partial1-partial2-partial3
        # if partial4 >= 0:
        #     # option1 = Line("Population", index, [data["revenue"]["population"]], ["Population"]).plot()
        #     # st_echarts(options=option1)

        #     col1, col2 = st.columns(2)

        #     with col1:
        #         option2 = Line("Biomassa", index, [data["revenue"]["biomassa"]], ["Biomassa (kg)"]).plot()
        #         st_echarts(options=option2)

        #     with col2:
        #         option3 = Line("Revenue", index, [data["revenue"]["revenue"], data["revenue"]["potential_revenue"]], 
        #         ["Realized Revenue", "Potential Revenue"], True).plot()
        #         st_echarts(options=option3)

        #     col11, col12 = st.columns(2)
        #     with col11:
        #         dataviz = [{"value": i[1], "name": data["index"][i[0]]} for i in enumerate(data["aggregate"])]
        #         option4 = Pie("Cost Structure Diagram", dataviz, True).plot()
        #         st_echarts(options=option4)
        #     with col12:
        #         # profit
        #         option5 = Line("Profit Margin", index, [data["data_profit"]["revenue"], data["data_profit"]["cost"], data["data_profit"]["profit"]],
        #                 ["Revenue", "Expense", "Profit"], True).plot()
        #         st_echarts(options=option5)
        # else:
        #     st.warning("Your partial harvest was wrong, the sum of partials is {} not matched".format(round(partial1*n0)+round(partial2*n0)+round(partial3*n0)+round(partial4*n0)) )

        # table = pd.DataFrame([
        #     ["Total Revenue", data["matrix"]["totalRevenue"]], 
        #     ["Total Expense", data["matrix"]["totalCost"]],
        #     ["Profit", data["matrix"]["profit"]],
        #     ["Margin", str(round(data["matrix"]["margin"] * 100, 2)) + "%"],
        #     ["Yeild", str(data["matrix"]["yeild"])],
        #     ["ADG", str(round(data["matrix"]["adg"], 2))],
        #     ["FCR", str(data["matrix"]["fcr"])]
        # ])

        # #function to hide index and columns in table
        # hide_table_row_index = """
        #     <style>
        #     thead {display:none}
        #     tbody th {display:none}
        #     .blank {display:none}
        #     </style>
        #     """
        
        # # Inject CSS with Markdown
        # st.markdown(hide_table_row_index, unsafe_allow_html=True)

        # st.table(table)
            