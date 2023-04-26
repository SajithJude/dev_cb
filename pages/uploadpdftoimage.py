import streamlit as st 
import io
import fitz
from PIL import Image
import os


def clear_images_folder():
    for file in os.listdir("images"):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            os.remove(os.path.join("images", file))


if not os.path.exists("images"):
    os.makedirs("images")


# upload file
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# check if a file was uploaded
if uploaded_file is not None:
    clear_images_folder()
    # read PDF file
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # display PDF file
    with fitz.open(uploaded_file.name) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)
            for image_index, img in enumerate(page.get_images(), start=1):
               

                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image = Image.open(io.BytesIO(image_bytes))
                image_filename = f"images/image_page{page_index}_{image_index}.{image_ext}"
                image.save(image_filename)

image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

# Create a dropdown menu to select an image
selected_image = st.selectbox("Choose an image to display:", image_files)

# Display the selected image
if selected_image:
    st.image(os.path.join("images", selected_image))

