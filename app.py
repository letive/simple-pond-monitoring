from vis_utils.sidebar import sidebar_head, sidebar_menu
from vis_utils.header import header_title
from controllers.parameter_estimation_v4 import base_section as bs1
from controllers.shrimp_weight import base_section as bs2
from controllers.unit_economic_model import base_section as bs3
import streamlit as st

sidebar_head()
# header_title()
menu = sidebar_menu()

if menu == "Main":
    pass
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
else:
    bs3()