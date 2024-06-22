import streamlit as st
from orchestrator.manage_docs import *

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
<div class="gradient-text">Q&A Docs</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)
user_input = st.text_input("Enter your question here:")

if st.button("Submit"):

    reply, metadata_source_page_to_return,URLs = search_docs(user_input)
    st.write(reply[0])
    references = ""
    markdown_references = ""
    for page,url in zip(metadata_source_page_to_return,URLs):

        if markdown_references == "":
            markdown_references += "### References\n"
            markdown_references += f"[{page}]({url})\n"
        else:
            markdown_references += f", [{page}]({url})\n"
    st.markdown(markdown_references)