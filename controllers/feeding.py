import streamlit as st
from streamlit_echarts import st_echarts
from lib.plot import Line
from lib.v2.feeding import get_rating_function, update_fr
import numpy as np
import pandas as pd

def base_section():
    
    # st.set_page_config(layout="wide")

    st.title("Feed Management")

    df = st.sidebar.file_uploader("Daily Shrimp Growth Data")
    sep1 = st.sidebar.text_input("Delimiter 1", value=",")
    with open("data/sample_data_input_feeding.csv") as f:
        st.sidebar.download_button('See the example of growth shrimp data', f, file_name='growth.csv')

    trays = st.sidebar.file_uploader("Feed Trays Monitoring")
    sep2 = st.sidebar.text_input("Delimiter 2", value=",")
    with open("data/sample_data_tray_input.csv") as f:
        st.sidebar.download_button('See the example of tray', f, file_name='trays.csv')

    no_of_feed = st.sidebar.number_input("Number of Feed per Day", value=4)

    set_columns = st.sidebar.expander("Set Columns")
    
    col_doc = set_columns.text_input("Column name of DOC", value="DOC")
    col_fr = set_columns.text_input("Column name of FR", value="formula_1")

    submit = st.sidebar.button("Submit")
    if submit:
        
        df = pd.read_csv(df, sep=sep1)
        trays = pd.read_csv(trays, sep=sep2)
        
        f_15_19, f_19_21, f_21_24, f_24_28, f_28_32, f_33, f_34 = get_rating_function(pd.read_csv("data/feed_table_temp.csv", sep=";"))
        f = [f_15_19, f_19_21, f_21_24, f_24_28, f_28_32, f_33, f_34]

        df[col_fr] = df[col_fr].str.replace("%", "").astype("float")

        ndf, next_fr = update_fr(df, trays, f, no_of_feed, col_doc, col_fr)

        st.metric("Next Feeding Recommendation", value=next_fr.round(2))

        plot, data = st.tabs(["Plot", "Data"])

        with plot:
            option = Line("Feeding Regime", x=df[col_doc].tolist(), y=[ndf[col_fr].tolist(), df[col_fr].tolist()], 
                labels=["After Adjustment", "Before Adjusment"], legend=True
            ).plot()
            option["color"] = ["#3AAE8E", "#fb0166"]
            st_echarts(options=option)


        with data:
            st.markdown("### Feed Rate After Adjustment")
            st.write(ndf)

            st.markdown("### Feed Rate Before Adjustment")
            st.write(df)


    # else:
    #     st.error("Something Wrong, Please report to the developer :)")





    