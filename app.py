from vis_utils.sidebar import sidebar_head, sidebar_menu
from vis_utils.header import header_title
from controllers.parameter_estimation_v4 import base_section as bs1
from controllers.shrimp_weight import base_section as bs2
from controllers.unit_economic_model import base_section as bs3
from controllers.main import base_section as bs4
from controllers.feeding import base_section as bs5
import streamlit as st
from streamlit_echarts import st_echarts

sidebar_head()
# header_title()
menu = sidebar_menu()

if menu == "Main":
    st.title("Metamorf Dashboard")
    bs4()

elif menu == "Model Validation":
    st.title("Model Validation")
    st.markdown(
        """
        This menu used to make a model validation about our model that was developed. This step is important, 
        because besides we know how effective the model, we also will get the greater alpha parameter that was estimated by system. 
        """
    )
    bs1()
elif menu == "Shrimp Growth Forecasting":
    bs2()
elif menu == "Feed Management":
    bs5()
else:
    bs3()