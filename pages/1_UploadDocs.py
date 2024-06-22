import streamlit as st
from pathlib import Path

from azure_blob.azure_blob_helper import AzureBlobHelper
from azure_blob.read_pdf import PDFHelper
from config import *
from orchestrator.manage_docs import *

SAVED_FOLDER = 'saved_files'

st.header("Upload Docs")
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

