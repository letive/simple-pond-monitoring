from vis_utils.sidebar import sidebar_head, sidebar_menu
from vis_utils.header import header_title
from controllers.parameter_estimation_v4 import base_section as bs1
from controllers.shrimp_weight import base_section as bs2
from controllers.unit_economic_model import base_section as bs3
from controllers.main import base_section as bs4
import streamlit as st
from streamlit_echarts import st_echarts

sidebar_head()
# header_title()
menu = sidebar_menu()

if menu == "Main":
    pass
    # st.title("Dashboard")
    # bs4()
    # col1, col2, col3 = st.columns([1,3,2])

    # with col1:
    #     st.markdown("metrik")
    
    # with col2:
    #     st_echarts(options={
    #             "title":{
    #                 "text":"Stacked Area Chart"
    #             },
    #             "tooltip":{
    #                 "trigger":"axis",
    #                 "axisPointer":{
    #                     "type":"cross",
    #                     "label":{
    #                         "backgroundColor":"#6a7985"
    #                     }
    #                 }
    #             },
    #             "legend":{
    #                 "data":[
    #                     "Email",
    #                     "Union Ads",
    #                     "Video Ads",
    #                     "Direct",
    #                     "Search Engine"
    #                 ]
    #             },
    #             "toolbox":{
    #                 "feature":{
    #                     "saveAsImage":{
                            
    #                     }
    #                 }
    #             },
    #             "grid":{
    #                 "left":"3%",
    #                 "right":"4%",
    #                 "bottom":"3%",
    #                 "containLabel":True
    #             },
    #             "xAxis":[
    #                 {
    #                     "type":"category",
    #                     "boundaryGap":False,
    #                     "data":[
    #                         "Mon",
    #                         "Tue",
    #                         "Wed",
    #                         "Thu",
    #                         "Fri",
    #                         "Sat",
    #                         "Sun"
    #                     ]
    #                 }
    #             ],
    #             "yAxis":[
    #                 {
    #                     "type":"value"
    #                 }
    #             ],
    #             "series":[
    #                 {
    #                     "name":"Email",
    #                     "type":"line",
    #                     "stack":"Total",
    #                     "areaStyle":{
                            
    #                     },
    #                     "emphasis":{
    #                         "focus":"series"
    #                     },
    #                     "data":[
    #                         120,
    #                         132,
    #                         101,
    #                         134,
    #                         90,
    #                         230,
    #                         210
    #                     ]
    #                 },
    #                 {
    #                     "name":"Union Ads",
    #                     "type":"line",
    #                     "stack":"Total",
    #                     "areaStyle":{
                            
    #                     },
    #                     "emphasis":{
    #                         "focus":"series"
    #                     },
    #                     "data":[
    #                         220,
    #                         182,
    #                         191,
    #                         234,
    #                         290,
    #                         330,
    #                         310
    #                     ]
    #                 },
    #                 {
    #                     "name":"Video Ads",
    #                     "type":"line",
    #                     "stack":"Total",
    #                     "areaStyle":{
                            
    #                     },
    #                     "emphasis":{
    #                         "focus":"series"
    #                     },
    #                     "data":[
    #                         150,
    #                         232,
    #                         201,
    #                         154,
    #                         190,
    #                         330,
    #                         410
    #                     ]
    #                 },
    #                 {
    #                     "name":"Direct",
    #                     "type":"line",
    #                     "stack":"Total",
    #                     "areaStyle":{
                            
    #                     },
    #                     "emphasis":{
    #                         "focus":"series"
    #                     },
    #                     "data":[
    #                         320,
    #                         332,
    #                         301,
    #                         334,
    #                         390,
    #                         330,
    #                         320
    #                     ]
    #                 },
    #                 {
    #                     "name":"Search Engine",
    #                     "type":"line",
    #                     "stack":"Total",
    #                     "label":{
    #                         "show":True,
    #                         "position":"top"
    #                     },
    #                     "areaStyle":{
                            
    #                     },
    #                     "emphasis":{
    #                         "focus":"series"
    #                     },
    #                     "data":[
    #                         820,
    #                         932,
    #                         901,
    #                         934,
    #                         1290,
    #                         1330,
    #                         1320
    #                     ]
    #                 }
    #             ]
    #             })

    # with col3:
    #     st_echarts(options={
    #         "tooltip":{
    #             "trigger":"item"
    #         },
    #         "legend":{
    #             "top":"5%",
    #             "left":"center"
    #         },
    #         "series":[
    #             {
    #                 "name":"Access From",
    #                 "type":"pie",
    #                 "radius":[
    #                     "40%",
    #                     "70%"
    #                 ],
    #                 "avoidLabelOverlap":False,
    #                 "label":{
    #                     "show":False,
    #                     "position":"center"
    #                 },
    #                 "emphasis":{
    #                     "label":{
    #                     "show":True,
    #                     "fontSize":"40",
    #                     "fontWeight":"bold"
    #                     }
    #                 },
    #                 "labelLine":{
    #                     "show":False
    #                 },
    #                 "data":[
    #                     {
    #                     "value":1048,
    #                     "name":"Search Engine"
    #                     },
    #                     {
    #                     "value":735,
    #                     "name":"Direct"
    #                     },
    #                     {
    #                     "value":580,
    #                     "name":"Email"
    #                     },
    #                     {
    #                     "value":484,
    #                     "name":"Union Ads"
    #                     },
    #                     {
    #                     "value":300,
    #                     "name":"Video Ads"
    #                     }
    #                 ]
    #             }]
    #         })

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