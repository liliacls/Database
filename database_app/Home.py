####################################################
# HOME PAGE : Lipid Database
####################################################

import streamlit as st

st.markdown("""
    <style>
    .module {
        border: 2px solid #1F77B4;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:#1F77B4">HOME</span> : BacLipidDB</span></h1>
    </div>
""", unsafe_allow_html=True)

st.write("")
st.write("Welcome to the Lipid Database application.")
st.write("Please select a module from the left menu.")