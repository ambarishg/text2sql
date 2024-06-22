import streamlit as st
import pandas as pd

import sys
sys.path.append('../')

from config import *
from azureopenaimanager.azureopenai_helper import *
from sqlmanager.azuresqlmanager import *

# Create a settings gear icon
def set_sql_settings():
    if 'show_settings' not in st.session_state:
            st.session_state.show_settings = False
    if 'server' not in st.session_state:
            st.session_state.server = server
    if 'database' not in st.session_state:
            st.session_state.database = database
    if 'username' not in st.session_state:
            st.session_state.username = username
    if 'password' not in st.session_state:
            st.session_state.password = password

set_sql_settings()

def toggle_settings():
        st.session_state.show_settings = not st.session_state.show_settings

st.button("⚙️ Settings", on_click=toggle_settings,
          help="Click to show/hide settings"
          )

if st.session_state.show_settings:
        with st.sidebar:
            st.header('Azure SQL Database Configuration')
            server2 = st.text_input('Server:', server)
            database2 = st.text_input('Database:', database)
            username2 = st.text_input('Username:', username)
            password2 = st.text_input('Password:', password, type='password')
            if st.button('Save settings'):
                st.session_state.server = server2
                st.session_state.database = database2
                st.session_state.username = username2
                st.session_state.password = password2


st.title('English as a Query Language')

user_input =st.text_input('Enter your query here:','How many suppliers are present ?')

if st.button('Submit'):
    try:
        # Create an instance of the AzureOpenAIManager
        azure_open_ai_manager = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                    api_version="2023-05-15"
                )
        msg,_,_,_ = azure_open_ai_manager.generate_answer_document(user_input)

        st.write(msg)

        if "```sql" not in msg:
            st.write("No SQL query found")
            
        else:
            query = msg.split("```sql")[1].split("```")[0].strip().replace("\n", " ")

            st.write("This is the SQL query generated by the model:")
            st.write(query)

            # Create an instance of the AzureSQLManager
            sql_helper = AzureSQLManager(st.session_state.server, \
                                     st.session_state.database, \
                                     st.session_state.username, \
                                     st.session_state.password)
            # Execute the query
            sql_helper.connect()
            results = sql_helper.execute_query_return(query)
            if results is None:
              st.write("No results found")
            else:
              st.write("This is the result of the query:")
              for row in results:
                st.write(row)
            sql_helper.disconnect()

    except Exception as e:
        st.write(e)