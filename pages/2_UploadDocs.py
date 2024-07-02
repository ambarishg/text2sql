import streamlit as st
import requests

if 'access_token' not in st.session_state:
    st.markdown("#### Please login to use this feature")
    st.stop()

SAVED_FOLDER = 'saved_files/'

gradient_text_html =  """<style>
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
<div class="gradient-text">Upload Docs</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)
uploaded_file = st.file_uploader(label = "Upload file", type=["pdf"])
category = st.text_input('Enter the category of the document')
short_description = st.text_input('Enter the short description of the document')

category = category.strip()
short_description = short_description.strip()

if uploaded_file is not None:
    if st.button('Save File'):
        
       files = {"file": uploaded_file}
       response = requests.post("http://localhost:8000/upload_docs/", files=files)
       if response.status_code == 200:
            st.success(f"File {uploaded_file.name} has been sent for processing \
                        successfully!")
       else:
            st.error("Upload failed.")


