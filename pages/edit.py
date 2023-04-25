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
    with fitz.open(uploaded_file.name) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)
            # st.write(image_list)
            if image_list:
                st.write(f"[+] Found a total of {len(image_list)} images in page {page_index}")
            else:
                st.write("[!] No images found on page", page_index)
            
            
            
            for image_index, img in enumerate(page.get_image_info(), start=1):
                st.write(img)

            #     # get the XREF of the image

                xref = img[xref]
                st.write(xref)
            #     # extract the image bytes
            #     base_image = pdf_file.extractImage(xref)
            #     image_bytes = base_image["image"]
            #     # get the image extension
            #     image_ext = base_image["ext"]
            #     # load it to PIL
            #     image = Image.open(io.BytesIO(image_bytes))
