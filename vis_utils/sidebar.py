import streamlit as st
import base64

@st.cache
def show_metamorf_logo(width, padding, margin):
    padding_top, padding_right, padding_bottom, padding_left = padding
    margin_top, margin_right, margin_bottom, margin_left = margin
    
    # link = 'http://sersitive.eu'
    
    with open('image/logo.png', 'rb') as f:
        data = f.read()
    
    bin_str = base64.b64encode(data).decode()
    html_code = f'''
                <img src="data:image/png;base64,{bin_str}"
                style="
                     margin: auto;
                     width: {width}%;
                     margin-top: {margin_top}px;
                     margin-right: {margin_right}px;
                     margin-bottom: {margin_bottom}px;
                     margin-left: {margin_left}%;
                     padding-top: {margin_top}px;
                     padding-right: {padding_right}px;
                     padding-bottom: {padding_bottom}px;
                     padding-left: {padding_left}%;
                     "/>
                '''

    return html_code

def sidebar_head():
    """
    Sets Page title, page icon, layout, initial_sidebar_state
    Sets position of radiobuttons (in a row or one beneath another)
    Shows logo in the sidebar
    """
    st.set_page_config(
        page_title="metamorf",
        page_icon="https://i.ibb.co/v424n70/logo-metamorf.png",
        layout="wide",
        initial_sidebar_state="auto"
    )

    st.set_option('deprecation.showfileUploaderEncoding', False)

    # SERSitivis logo
    html_code = show_metamorf_logo(100, [1, 1, 1, 1], margin=[0, 0, 0, 0])
    st.sidebar.markdown(html_code, unsafe_allow_html=True)
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('---')

def sidebar_menu():
    menu = st.sidebar.selectbox("Select Menu", ["Farm Economics", "Model Validation", "Shrimp Growth Forecasting", "Unit Economic Model", "Feed Management"])
    return menu
