from lib.body_weight import body_weight_section
from lib.versi2 import version_2
import streamlit as st

version = st.sidebar.radio("Select version", ("v1", "v2"))

if version == "v1":
    body_weight_section()
elif version == "v2":
    version_2()
