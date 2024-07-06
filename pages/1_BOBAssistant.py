import streamlit as st
import pandas as pd
import requests

import sys
sys.path.append('../')

if 'access_token' not in st.session_state:
    st.markdown("#### Please login to use this feature")
    st.stop()


show_SQL = st.checkbox("Show SQL",True)
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
<div class="gradient-text">Talk in English with Data</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)

user_input =st.text_input('Enter your query here:','How many suppliers are present ?')

if st.button('Submit'):
    try:
        
        response = requests.post("http://localhost:8000/get_sql_results/", 
                                    json={"query": user_input})
        
        data = response.json()

        sql_str = data.get("sql_query")
        df = pd.DataFrame(data.get("dataframe"))
        
        if show_SQL:
            st.write(data.get("sql_query"))
        
        if not sql_str:
            st.write("No SQL query found")
            
        if df is None:
            st.write("No results found")
        else:
            st.write("This is the result of the query:")
            st.dataframe(df)
    except Exception as e:
        st.write(e)

        
    