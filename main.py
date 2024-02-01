import streamlit as st
from solution import optimize_price

sku_code = st.text_input('Enter sku code', 'SIK-123')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    original_price, recommendation = optimize_price(uploaded_file, sku_code)
    st.write('Original price: ', original_price)
    st.write('Recommended price:', recommendation)
