import streamlit as st
from PIL import Image
import base64

# Open the image file and encode it as a base64 string
def encode_image(data):
    return base64.b64encode(data).decode("utf-8")

st.title("Image Analysis")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    encoded_image = encode_image(image.tobytes())
    print(encoded_image)