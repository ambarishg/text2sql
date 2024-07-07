import streamlit as st
from PIL import Image
from orchestrator.manage_docs import *
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

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
<div class="gradient-text">Show Files</div>
"""
st.write(gradient_text_html, unsafe_allow_html=True)

response =  requests.post("http://localhost:8000/get_files_indexed/")
data = response.json()


li_indexed_files = data.get("file_list")

df_indexed_files = pd.DataFrame(li_indexed_files, columns=['File Name'])

# Configure AgGrid options
gb = GridOptionsBuilder.from_dataframe(df_indexed_files)
gb.configure_selection('multiple', use_checkbox=True, 
                       groupSelectsChildren=True)
gridOptions = gb.build()

# Display the table
response = AgGrid(
    df_indexed_files,
    gridOptions=gridOptions,
    data_return_mode=DataReturnMode.AS_INPUT,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    theme= 'material',  # Add theme color to the table
    enable_enterprise_modules=True,
    width='100%',
    reload_data=True
)

# Get selected rows
selected_rows = response['selected_rows']

try:
    if len(selected_rows) == 0:
        st.markdown("#### Please select a file to view")
        st.stop()
    else:
        st.markdown("#### Selected Files")
        selected_df = pd.DataFrame(selected_rows)
        for row in selected_df.iterrows():
            st.write(row[1]['filename'])
except Exception as e:
    pass

    