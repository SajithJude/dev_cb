# import streamlit as st 
# import io
# import fitz
# from PIL import Image
# import os


# if not os.path.exists("images"):
#     os.makedirs("images")


# # upload file
# uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# # check if a file was uploaded
# if uploaded_file is not None:
#     # read PDF file
#     with open(uploaded_file.name, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     # display PDF file
#     with fitz.open(uploaded_file.name) as doc:
#         for page_index in range(len(doc)):
#             page = doc[page_index]
#             image_list = page.get_images(full=True)
#             # st.write(image_list)
#             if image_list:
#                 st.write(f"[+] Found a total of {len(image_list)} images in page {page_index}")
#             else:
#                 st.write("[!] No images found on page", page_index)
            
            
            
#             for image_index, img in enumerate(page.get_images(), start=1):
#                 st.write(img)

#             #     # get the XREF of the image

#                 xref = img[0]
#                 st.write(xref)
#             #     # extract the image bytes
#                 base_image = doc.extract_image(xref)
#                 image_bytes = base_image["image"]
#             #     # get the image extension
#                 image_ext = base_image["ext"]
#             #     # load it to PIL
#                 image = Image.open(io.BytesIO(image_bytes))
#                 image_filename = f"images/image_page{page_index}_{image_index}.{image_ext}"
#                 image.save(image_filename)
#                 st.success(f"{image_filename} saved successfully")

#                 # st.image(image)

# image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

# # Create a dropdown menu to select an image
# selected_image = st.selectbox("Choose an image to display:", image_files)

# # Display the selected image
# if selected_image:
#     st.image(os.path.join("images", selected_image))



import streamlit as st
import json
import os
from itertools import cycle


def update_json(topic_data):
    with open("output.json", "w") as f:
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)

def select_images(images):
    selected_images = []
    for image in images:
        col1, col2 = st.columns([1, 3])
        col1.image(image, use_column_width=True)
        checkbox = col2.checkbox("", key=image)
        if checkbox:
            selected_images.append(image)
    return selected_images

json_data = '''
{
  "Topics": [
    {
      "What is Strategy and Why is it Important?": [
        "Michael E. Porter’s Definition of Strategy",
        "Eric T. Anderson and Duncan Simester’s Step-by-Step Guide to Smart Business Experiments",
        "Jan Rivkin’s Alternative Approach to Making Strategic Choices",
        "Shona L. Brown and Kathleen M. Eisenhardt’s Competing on the Edge: Strategy as Structured Chaos",
        "Cynthia A. Montgomery’s Putting Leadership Back into Strategy"
      ]
    },
    {
      "The Evolution of Strategic Management": [
        "The Economist’s Definition of Strategy",
        "Mintzberg’s 10 Schools of Thought for Strategy Formulation",
        "Mintzberg’s 5 Ps of Strategy"
      ]
    },
    {
      "Strategy vs Tactics": [
        "Definition of Strategy",
        "Definition of Tactics",
        "Differences between Strategy and Tactics"
      ]
    }
  ]
}
'''

col1, col2 = st.columns(2)
data = json.loads(json_data)
images = ["https://media.istockphoto.com/id/1155021690/photo/sri-dalada-maligawa-or-the-temple-of-the-sacred-tooth-relic-kandy-sri-lanka.jpg?s=170667a&w=is&k=20&c=lsRo82JVGY1e3l6d7Dh2cu_mMIIdr-jDRun-bVaLhNM=","https://upload.wikimedia.org/wikipedia/commons/5/56/Sri_Lanka_-_029_-_Kandy_Temple_of_the_Tooth.jpg","https://static.wixstatic.com/media/65f045_e4c0db99c4294f6194d270687add03f6~mv2.jpg/v1/crop/x_0,y_51,w_1105,h_469/fill/w_560,h_260,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/kandy_polwaththa_srilanka_jpeg.jpg", "https://images.pexels.com/photos/268533/pexels-photo-268533.jpeg?cs=srgb&dl=pexels-pixabay-268533.jpg&fm=jpg","https://media.istockphoto.com/id/629022568/photo/branching-moonlight.jpg?s=612x612&w=0&k=20&c=pECtItfnKuOC-RIzGXk1tQfzWSetMEmwiQCX5msooxg=" ]
topic_data = {list(t.keys())[0]: list(t.values())[0] for t in data["Topics"]}
if "topic_data" not in st.session_state:
      st.session_state['topic_data'] = topic_data
col1.title("Topics and Subtopics Editor")

topic_name = col1.text_input("Enter topic name:")

if col1.button("Save Topic"):
    if topic_name not in st.session_state['topic_data']:
        st.session_state['topic_data'][topic_name] = []
        update_json(topic_data)

topic_options = list(st.session_state['topic_data'].keys())
selected_topic = col1.selectbox("Select a topic:", topic_options)

subtopics = st.session_state['topic_data'][selected_topic]

col1.write("## Subtopics:")
subtopics_input = col1.multiselect("", subtopics, default=subtopics)

if col1.button("Save Subtopics"):
    st.session_state['topic_data'][selected_topic] = subtopics_input
    update_json(st.session_state['topic_data'])
add = col1.button("Add Subtopic")
if "add" in st.session_state  or add:
    st.session_state['add'] = True
    new_subtopic = col1.text_input("Enter subtopic name:")
    if col1.button("Update"):
        if new_subtopic not in st.session_state['topic_data'][selected_topic]:
            st.session_state['topic_data'][selected_topic].append(new_subtopic)
            #col1.write(st.session_state['topic_data'][selected_topic])
            #update_json(st.session_state['topic_data'])
            add= None
            st.session_state['add'] = False
            st.experimental_rerun()


image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

selected_images = []
for image in image_files:
    cols = cycle(st.columns(4))
    for idx, image in enumerate(image_files):
        next(cols).image(os.path.join("images", image), width=150, caption=caption[idx])
        checkbox = colu1.checkbox("", key=str(image))
        colu2.image(os.path.join("images", image), use_column_width=True)


filteredImages = [] # your images here
caption = [] # your caption here
cols = cycle(st.columns(4)) # st.columns here since it is out of beta at the time I'm writing this
for idx, filteredImage in enumerate(filteredImages):
    next(cols).image(filteredImage, width=150, caption=caption[idx])



    if checkbox:
        selected_images.append(image)

if selected_images:
    col1.write("Selected Images:")
    for image in selected_images:

        col1.image(os.path.join("images", image), width=100)

col2.write("## Updated JSON:")
col2.json({"Topics": [{k: v} for k, v in st.session_state['topic_data'].items()]})

