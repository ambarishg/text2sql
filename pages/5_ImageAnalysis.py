import streamlit as st
from PIL import Image
import requests

if 'access_token' not in st.session_state:
    st.markdown("#### Please login to use this feature")
    st.stop()

gradient_text_html = """<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, #BA4A00  , #EDBB99);
    background: linear-gradient(to right, #BA4A00  , #EDBB99);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline;
    font-size: 3em;
}
</style>
<div class="gradient-text">Image Analysis</div>
"""
st.write(gradient_text_html, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    files = {"file": uploaded_file.getvalue()}
    response =  requests.post("http://localhost:8000/get_image_analysis/", 
                              files=files)
    
    st.write(response)
    st.write(response.json())