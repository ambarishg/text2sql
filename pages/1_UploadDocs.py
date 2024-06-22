import streamlit as st
from pathlib import Path

from azure_blob.azure_blob_helper import AzureBlobHelper
from azure_blob.read_pdf import PDFHelper
from config import *
from orchestrator.manage_docs import *

SAVED_FOLDER = 'saved_files'

gradient_text_html = """<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, blue, lightblue);
    background: linear-gradient(to right, blue, lightblue);
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
if uploaded_file is not None:
    if st.button('Save File'):
        save_path = Path(SAVED_FOLDER, uploaded_file.name)
        with open(save_path, mode='wb') as w:
            w.write(uploaded_file.getvalue())
        upload_docs(SAVED_FOLDER, uploaded_file.name)
        
        st.success('File uploaded successfully')
        st.balloons()

