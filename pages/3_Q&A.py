import streamlit as st
import requests

if 'access_token' not in st.session_state:
    st.markdown("#### Please login to use this feature")
    st.stop()

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
<div class="gradient-text">Q&A with Docs</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)
user_input = st.text_input("Enter your question here:",
                           "What is Segmentation?")

if st.button("Submit"):
    
    response =  requests.post("http://localhost:8000/get_answer_from_question/", 
                              json={"query": user_input})
    data = response.json()

    reply = data.get("reply")
    metadata_source_page_to_return = data.get("metadata_source_page_to_return")
    URLs = data.get("URLs")
    reranker_score = data.get("reranker_confidence")

    st.write(reply)
    references = ""
    markdown_references = ""
    for page,url in zip(metadata_source_page_to_return,URLs):

        if markdown_references == "":
            markdown_references += "### References\n"
            markdown_references += f"[{page}]({url})\n"
        else:
            markdown_references += f", [{page}]({url})\n"
    st.markdown(markdown_references)

    st.markdown(f"Reranker score: {reranker_score}")
