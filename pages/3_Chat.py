import streamlit as st
from orchestrator.manage_docs import *
from streamlit_chat import message

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
<div class="gradient-text">Chat with Docs</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)

user_input = st.text_input("Your Question","")
if user_input !='':
    reply, metadata_source_page_to_return,URLs = search_docs(user_input)

    references = ""
    markdown_references = ""
    for page,url in zip(metadata_source_page_to_return,URLs):

        if markdown_references == "":
            markdown_references += "### References\n"
            markdown_references += f"[{page}]({url})\n"
        else:
            markdown_references += f", [{page}]({url})\n"
    
    
    
    if 'generated' not in st.session_state:
            st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    st.session_state.past.append(user_input)
    st.session_state.generated.append(reply[0])
    st.markdown(markdown_references)

    if st.session_state['generated']:    
        for i in range(len(st.session_state['generated'])-1, -1, -1):

            message(st.session_state["generated"][i], key="AZUREAI-VECTORSEARCH" + str(i))
            message(st.session_state['past'][i], is_user=True, key="AZUREAI-VECTORSEARCH" + str(i) + "_user")
    