import streamlit as st
from vis_utils.sidebar import show_metamorf_logo

def header_logo():
    html_code = show_metamorf_logo(100, [1, 1, 1, 1], margin=[0, 0, 0, 0])
    st.markdown(html_code, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')

def header_title():
    st.title("Metamorf")
    st.text("Analysis & Forecast")