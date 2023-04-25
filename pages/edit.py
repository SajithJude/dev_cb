import streamlit as st 
import io
import fitz
from PIL import Image



import streamlit as st

# upload file
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# check if a file was uploaded
if uploaded_file is not None:
    # read PDF file
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # display PDF file
    import fitz
    with fitz.open(uploaded_file.name) as doc:
        for page in doc:
            st.image(page.get_pixmap())
