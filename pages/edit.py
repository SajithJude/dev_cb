

import streamlit as st
import json
import os
from itertools import cycle
import glob


def update_json(topic_data):
    with open("output.json", "w") as f:
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)


def find_images():
    image_exts = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
    image_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(image_exts):
                image_files.append(os.path.join(root, file))
    return image_files


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

col1, col2,col3 = st.columns(3)

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





col3.write("## Images")
image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
selected_images = []
# for image in image_files:
expander = col1.expander("Select images")
n_pages = 20

image_exts = ["png", "jpg", "jpeg", "tiff", "bmp", "gif"]
page_index = col3.slider("Select page number", 1, n_pages)

with col3.expander(f"Page {page_index}", expanded=True):
    image_files = [f for ext in image_exts for f in glob.glob(f"images/image_page{page_index}_*.{ext}")]
    if image_files:
        for image_filename in image_files:
            if os.path.isfile(image_filename):
                st.image(image_filename, caption=os.path.basename(image_filename))
            else:
                st.warning(f"Image not found: {os.path.basename(image_filename)}")
    else:
        st.warning("No images found for this page.")


col2.write("## Updated JSON:")
col2.json({"Topics": [{k: v} for k, v in st.session_state['topic_data'].items()]})




all_image_files = find_images()

# Create a dropdown menu to select an image
selected_image = st.selectbox("Choose an image to display:", all_image_files)
if selected_image:

  st.image(os.path.join("images", sel_page))
