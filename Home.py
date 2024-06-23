import streamlit as st
import msal
import requests
from config import * 

# Define your Azure AD credentials
CLIENT_ID = CLIENT_ID
CLIENT_SECRET = CLIENT_SECRET
TENANT_ID = TENANT_ID
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_URI = 'http://localhost:8501'
SCOPE = ['User.Read']

# Initialize the MSAL confidential client application
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# Function to get the authorization URL
def get_auth_url():
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return auth_url

# Function to get the token
def get_token(auth_code):
    token_response = msal_app.acquire_token_by_authorization_code(
        auth_code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return token_response

# Streamlit application
st.title('Bank of Baroda Assistant')


if 'access_token' not in st.session_state:
    auth_code = st.query_params.get_all(key = 'code')

    if auth_code:
        token_response = get_token(auth_code[0])
        if 'access_token' in token_response:
            st.session_state['access_token'] = token_response['access_token']
            st.query_params.clear()  # Clear query parameters after login
            st.success('Login successful!')
        else:
            st.error('Login failed')
    else:
        auth_url = get_auth_url()
        st.markdown(f'[Login with Azure AD]({auth_url})')
else:
    st.success('You are logged in!')


if st.button('Logout'):
    del st.session_state['access_token']
    st.query_params.clear()  # Clear query parameters after logout
    st.success('You have logged out')
