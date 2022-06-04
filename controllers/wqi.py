import streamlit as st
import pandas as pd
import numpy as np
from lib.wqi import Scoring, water_quality_index, betha_wqi
from lib.plot import Line
from streamlit_echarts import st_echarts

def wqi_dash():

    st.title("Water Quality Index")
    
    st.sidebar.markdown("## Upload Data")
    bio = st.sidebar.file_uploader("Biological Data")
    with open("data/data_sample - biological.csv") as f:
        st.sidebar.download_button('See the example of biological data', f, file_name='biological.csv')

    chem = st.sidebar.file_uploader("Chemical Data")
    with open("data/data_sample - chemical.csv") as f:
        st.sidebar.download_button('See the example of chemical data', f, file_name='chemical.csv')
    
    st.sidebar.markdown("## pH")
    ph_suitable_min = st.sidebar.number_input("pH suitable min", value=7.5, step=1.,format="%.2f") 
    ph_suitable_max = st.sidebar.number_input("pH suitable max", value=8.5, step=1.,format="%.2f") 
    ph_optimal_min = st.sidebar.number_input("pH optimal min", value=7.7, step=1.,format="%.2f") 
    ph_optimal_max = st.sidebar.number_input("pH optimal max", value=8.3, step=1.,format="%.2f")
    ph_upper_limit = st.sidebar.number_input("pH upper limit", value=14.0, step=1.,format="%.2f") 
    ph_weight = st.sidebar.number_input("weight of pH", value=1.0, step=1.,format="%.2f") 

    st.sidebar.markdown("## Temperature")
    temp_suitable_min = st.sidebar.number_input("Temperature suitable min", value=25.0, step=1.,format="%.2f") 
    temp_suitable_max = st.sidebar.number_input("Temperature suitable max", value=33.0, step=1.,format="%.2f") 
    
    temp_optimal_min = st.sidebar.number_input("Temperature optimal min", value=28.0, step=1.,format="%.2f") 
    temp_optimal_max = st.sidebar.number_input("Temperature optimal max", value=32.0, step=1.,format="%.2f")

    temp_upper_limit = st.sidebar.number_input("Temperature upper limit", value=36.0, step=1.,format="%.2f")
    temp_weight = st.sidebar.number_input("weight of temperature", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## Salinity")
    sal_suitable_min = st.sidebar.number_input("Salinity suitable min", value=10.0, step=1.,format="%.2f") 
    sal_suitable_max = st.sidebar.number_input("Salinity suitable max", value=35.0, step=1.,format="%.2f") 
    
    sal_optimal_min = st.sidebar.number_input("Salinity optimal min", value=20.0, step=1.,format="%.2f") 
    sal_optimal_max = st.sidebar.number_input("Salinity optimal max", value=30.0, step=1.,format="%.2f")

    sal_upper_limit = st.sidebar.number_input("Salinity upper limit", value=45.0, step=1.,format="%.2f") 

    sal_weight = st.sidebar.number_input("weight of salinity", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## Dissolved Oxygen")
    do_suitable_min = st.sidebar.number_input("DO suitable min", value=4.0, step=1.,format="%.2f") 
    do_suitable_max = st.sidebar.number_input("DO suitable max", value=10.0, step=1.,format="%.2f") 
    
    do_optimal_min = st.sidebar.number_input("DO optimal min", value=6.0, step=1.,format="%.2f") 
    do_optimal_max = st.sidebar.number_input("DO optimal max", value=9.0, step=1.,format="%.2f")

    do_upper_limit = st.sidebar.number_input("DO upper limit", value=10.0, step=1.,format="%.2f") 
    do_weight = st.sidebar.number_input("weight of DO", value=1.0, step=1.,format="%.2f")  

    # st.sidebar.markdown("## Unionized Ammonia")
    # ua_suitable_min = st.sidebar.number_input("UA suitable min", value=0.0, step=1.,format="%.2f") 
    # ua_suitable_max = st.sidebar.number_input("UA suitable max", value=0.16, step=1.,format="%.2f") 
    
    # ua_optimal_min = st.sidebar.number_input("UA optimal min", value=0.0001, step=1.,format="%.2f") 
    # ua_optimal_max = st.sidebar.number_input("UA optimal max", value=0.06, step=1.,format="%.2f")

    # ua_upper_limit = st.sidebar.number_input("UA upper limit", value=1.0, step=1.,format="%.2f") 
    # ua_weight = st.sidebar.number_input("weight of UA", value=1.0, step=1.,format="%.2f")  


    st.sidebar.markdown("## Alkalinity")
    al_suitable_min = st.sidebar.number_input("Alkalinity suitable min", value=75.0, step=1.,format="%.2f") 
    al_suitable_max = st.sidebar.number_input("Alkalinity suitable max", value=250.0, step=1.,format="%.2f") 
    
    al_optimal_min = st.sidebar.number_input("Alkalinity optimal min", value=120.0, step=1.,format="%.2f") 
    al_optimal_max = st.sidebar.number_input("Alkalinity optimal max", value=200.0, step=1.,format="%.2f")

    al_upper_limit = st.sidebar.number_input("Alkalinity upper limit", value=300.0, step=1.,format="%.2f") 
    al_weight = st.sidebar.number_input("weight of alkalinity", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## $NO_2$ (Nitrit)")
    no2_suitable_min = st.sidebar.number_input("Nitrit suitable min", value=0.0, step=1.,format="%.2f") 
    no2_suitable_max = st.sidebar.number_input("Nitrit suitable max", value=4.0, step=1.,format="%.2f") 
    
    no2_optimal_min = st.sidebar.number_input("Nitrit optimal min", value=0.001, step=1.,format="%.2f") 
    no2_optimal_max = st.sidebar.number_input("Nitrit optimal max", value=0.38, step=1.,format="%.2f")

    no2_upper_limit = st.sidebar.number_input("Nitrit upper limit", value=8.0, step=1.,format="%.2f") 

    no2_weight = st.sidebar.number_input("weight of Nitrit", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## $NO_3$ (Nitrat)")
    no3_suitable_min = st.sidebar.number_input("Nitrat suitable min", value=0.0, step=1.,format="%.2f") 
    no3_suitable_max = st.sidebar.number_input("Nitrat suitable max", value=220.0, step=1.,format="%.2f") 
    
    no3_optimal_min = st.sidebar.number_input("Nitrat optimal min", value=0.001, step=1.,format="%.2f") 
    no3_optimal_max = st.sidebar.number_input("Nitrat optimal max", value=60.0, step=1.,format="%.2f")

    no3_upper_limit = st.sidebar.number_input("Nitrat upper limit", value=250.0, step=1.,format="%.2f") 
    no3_weight = st.sidebar.number_input("weight of Nitrat", value=1.0, step=1.,format="%.2f")  

    st.sidebar.markdown("## $NH_4$ (Ammonium)")
    nh4_suitable_min = st.sidebar.number_input("Ammonium suitable min", value=0.25, step=1.,format="%.2f") 
    nh4_suitable_max = st.sidebar.number_input("Ammonium suitable max", value=6.0, step=1.,format="%.2f") 
    
    nh4_optimal_min = st.sidebar.number_input("Ammonium optimal min", value=0.0, step=1.,format="%.2f") 
    nh4_optimal_max = st.sidebar.number_input("Ammonium optimal max", value=0.25, step=1.,format="%.2f")

    nh4_upper_limit = st.sidebar.number_input("Ammonium upper limit", value=30.0, step=1.,format="%.2f")
    nh4_weight = st.sidebar.number_input("weight of Ammonium", value=1.0, step=1.,format="%.2f")

    st.sidebar.markdown("## Total Organic Matter (TOM)")
    tom_suitable_min = st.sidebar.number_input("TOM suitable min", value=50.0, step=1.,format="%.2f") 
    tom_suitable_max = st.sidebar.number_input("TOM suitable max", value=90.0, step=1.,format="%.2f") 
    
    tom_optimal_min = st.sidebar.number_input("TOM optimal min", value=0.0, step=1.,format="%.2f") 
    tom_optimal_max = st.sidebar.number_input("TOM optimal max", value=50.0, step=1.,format="%.2f")

    tom_upper_limit = st.sidebar.number_input("TOM upper limit", value=500.0, step=1.,format="%.2f")
    tom_weight = st.sidebar.number_input("weight of TOM", value=1.0, step=1.,format="%.2f")

    st.sidebar.markdown("## Total Plankton")
    plank_suitable_min = st.sidebar.number_input("Plankton suitable min", value=50000.0, step=1.,format="%.2f") 
    plank_suitable_max = st.sidebar.number_input("Plankton suitable max", value=500000.0, step=1.,format="%.2f") 
    
    plank_optimal_min = st.sidebar.number_input("Plankton optimal min", value=100000.0, step=1.,format="%.2f") 
    plank_optimal_max = st.sidebar.number_input("Plankton optimal max", value=250000.0, step=1.,format="%.2f")

    plank_upper_limit = st.sidebar.number_input("Plankton upper limit", value=1000000.0, step=1.,format="%.2f")
    plank_weight = st.sidebar.number_input("weight of Plankton", value=1.0, step=1.,format="%.2f")
    
    submit = st.sidebar.button("submit")

    if submit:
        if (bio is not None) & (chem is not None):
            # st.write("Biological Data")
            bio_df = pd.read_csv(bio)
            bio_df.fillna(np.nan, inplace=True)
            # st.write(bio_df)

            # st.write("Chemical Data")
            chem_df = pd.read_csv(chem)
            chem_df.replace("-", np.nan, inplace=True)
            bio_df.fillna(np.nan, inplace=True)
            # df.replace(to_replace=[None], value=np.nan, inplace=True)
            # st.write(chem_df)

            df = pd.DataFrame()

            data = Scoring(bio_df, chem_df)

            ph_m, ph_a, w_ph_m, w_ph_a  = data._pH(ph_suitable_min, ph_suitable_max, ph_optimal_min, 
                                    ph_optimal_max, ph_upper_limit, ph_weight)
            
            df["ph_score_m"] = ph_m 
            df["w_ph_score_m"] = w_ph_m
            df["ph_score_a"] = ph_a
            df["w_ph_score_a"] = w_ph_a
            df["weight_ph"] = ph_weight

            del ph_m 
            del w_ph_m
            del ph_a 
            del w_ph_a

            temp_m, temp_a, w_temp_m, w_temp_a  = data._temperature(temp_suitable_min, temp_suitable_max, temp_optimal_min, 
                                    temp_optimal_max, temp_upper_limit, temp_weight)
            
            df["temperature_score_m"] = temp_m 
            df["w_temp_m"] = w_temp_m
            df["temperature_score_a"] = temp_a
            df["w_temp_a"] = w_temp_a
            df["weight_temperature"] = temp_weight

            del temp_m 
            del w_temp_m
            del temp_a 
            del w_temp_a

            sal_m, sal_a, w_sal_m, w_sal_a  = data._salinity(sal_suitable_min, sal_suitable_max, sal_optimal_min, 
                                    sal_optimal_max, sal_upper_limit, sal_weight)

            df["sal_score_m"] = sal_m 
            df["w_sal_score_m"] = w_sal_m
            df["sal_score_a"] = sal_a
            df["w_sal_score_a"] = w_sal_a
            df["weight_salinity"] = sal_weight

            del sal_m 
            del w_sal_m
            del sal_a 
            del w_sal_a

            # chemistry

            do_s, do_m, w_do_s, w_do_m  = data._do(do_suitable_min, do_suitable_max, do_optimal_min, 
                                    do_optimal_max, do_upper_limit, do_weight)

            df["do_score_s"] = do_s 
            df["w_do_score_s"] = w_do_s
            df["do_score_m"] = do_m
            df["w_do_score_m"] = w_do_m
            df["weight_do"] = do_weight

            del do_s 
            del w_do_s
            del do_m 
            del w_do_m

            alk, w_alk = data._alkalinity(al_suitable_min, al_suitable_max, al_optimal_min,
                    al_optimal_max, al_upper_limit, al_weight)
            
            df["alkaline_score"] = alk
            df["w_alkaline_score"] = w_alk 
            df["weight_alkaline"] = al_weight

            del alk
            del w_alk

            no2_m, no2_a, w_no2_m, w_no2_a = data._no2(no2_suitable_min, no2_suitable_max, no2_optimal_min,
                                        no2_optimal_max, no2_upper_limit, no2_weight)
            
            df["no2_score_m"] = no2_m
            df["w_no2_score_m"] = w_no2_m
            df["no2_score_a"] = no2_a
            df["w_no2_score_a"] = w_no2_a 
            df["weight_no2"] = no2_weight

            del no2_m
            del no2_a
            del w_no2_m
            del w_no2_a

            no3_m, no3_a, w_no3_m, w_no3_a = data._no3(no3_suitable_min, no3_suitable_max, no3_optimal_min,
                                        no3_optimal_max, no3_upper_limit, no3_weight)
            
            df["no3_score_m"] = no3_m
            df["w_no3_score_m"] = w_no3_m
            df["no3_score_a"] = no3_a
            df["w_no3_score_a"] = w_no3_a
            df["weight_no3"] = no3_weight

            del no3_m
            del w_no3_m
            del no3_a
            del w_no3_a

            nh_m, nh_a, w_nh_m, w_nh_a = data._nh4(nh4_suitable_min, nh4_suitable_max, nh4_optimal_min,
                                        nh4_optimal_max, nh4_upper_limit, nh4_weight)
            
            df["nh4_score_m"] = nh_m
            df["w_nh4_score_m"] = w_nh_m
            df["nh4_score_a"] = nh_a
            df["w_nh4_score_a"] = w_nh_a
            df["weight_nh4"] = nh4_weight

            del nh_m
            del nh_a
            del w_nh_m
            del w_nh_a

            tom_m, w_tom_m = data._tom(tom_suitable_min, tom_suitable_max, tom_optimal_min,
                        tom_optimal_max, tom_upper_limit, tom_weight)
            
            df["tom_score_m"] = tom_m
            df["w_tom_score_m"] = w_tom_m
            df["weight_tom"] = tom_weight

            del tom_m
            del w_tom_m

            plank_m, plank_a, w_plank_m, w_plank_a = data._plankton(plank_suitable_min, plank_suitable_max,
                                        plank_optimal_min, plank_optimal_max, plank_upper_limit, plank_weight)

            df["plankton_score_m"] = plank_m
            df["w_plankton_score_m"] = w_plank_m
            df["plankton_score_a"] = plank_a
            df["w_plankton_score_a"] = w_plank_a
            df["weight_plankton"] = plank_weight

            del w_plank_m
            del w_plank_a
            del plank_m
            del plank_a

            quality, alert = water_quality_index(df)

            option = Line("WQI Alpha", bio_df["Tanggal"].tolist(), [quality, alert], ["WQI", "Alert"], True).plot()
            
            st_echarts(options=option)

            beta_score = betha_wqi(df)
            option2 = Line("WQI Beta", bio_df["Tanggal"].tolist(), [beta_score], ["WQI"], True).plot()
            st_echarts(options=option2)

            # single_score_type = st.selectbox('Pilih item', ['pH', 'Temperature', "Salinity", "DO", "Alkalinity", "Nitrit", "Nitrat", "NH4", "TOM", "Plankton"])
        
            st.markdown("### Single Item Scoring")

            # if single_score_type == "pH":
            with st.expander("pH"):
                st_echarts(
                    options=Line("pH", bio_df["Tanggal"].tolist(), [df["ph_score_a"].tolist(), df["ph_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "Temperature":
            with st.expander("Temperature"):
                st_echarts(
                    options=Line("Temperature", bio_df["Tanggal"].tolist(), [df["temperature_score_a"].tolist(), df["temperature_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "Salinity":
            with st.expander("Salinity"):
                st_echarts(
                    options=Line("Salinity", bio_df["Tanggal"].tolist(), [df["sal_score_a"].tolist(), df["sal_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "DO":
            with st.expander("Dissolve Oxygen"):
                st_echarts(
                    options=Line("DO", bio_df["Tanggal"].tolist(), [df["do_score_s"].tolist(), df["do_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "Alkalinity":
            with st.expander("Alkalinity"):
                st_echarts(
                    options=Line("Alkalinity", bio_df["Tanggal"].tolist(), [df["alkaline_score"].tolist()], ["Score"], True).plot()
                )
            # elif single_score_type == "Nitrit":
            with st.expander("Nitrit"):
                st_echarts(
                    options=Line("Nitrit", bio_df["Tanggal"].tolist(), [df["no2_score_a"].tolist(), df["no2_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "Nitrat":
            with st.expander("Nitrat"):
                st_echarts(
                    options=Line("Nitrat", bio_df["Tanggal"].tolist(), [df["no3_score_a"].tolist(), df["no3_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "NH4":
            with st.expander("NH4"):
                st_echarts(
                    options=Line("NH4", bio_df["Tanggal"].tolist(), [df["nh4_score_a"].tolist(), df["nh4_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # elif single_score_type == "TOM":
            with st.expander("Total Organic Matter"):
                st_echarts(
                    options=Line("TOM", bio_df["Tanggal"].tolist(), [df["tom_score_m"].tolist()], ["Score"], True).plot()
                )
            # elif single_score_type =="Plankton":
            with st.expander("Plankton"):
                st_echarts(
                    options=Line("Plankton", bio_df["Tanggal"].tolist(), [df["plankton_score_a"].tolist(), df["plankton_score_m"].tolist()], ["Afternoon", "Morning"], True).plot()
                )
            # else:
            #     st_echarts(
            #         options=Line("Plankton", bio_df["Tanggal"].tolist(), [df["plankton_score_a"].tolist(), df["plankton_score_a"].tolist()], ["Afternoon", "Morning"], True).plot()
            #     )

            st.markdown("### Raw Data")
            col1, col2 = st.columns(2)
            with col1:
                st.write("biological data")
                st.write(bio_df)
            with col2:
                st.write("chemical data")
                st.write(chem_df)

            st.download_button("Download for the computational result", df.to_csv(), "data_scoring.csv", "text/csv", key='download-csv')
        
        else:
            st.warning("Error. Maybe the system is error or you didn't upload data yet")