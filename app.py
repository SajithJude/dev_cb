import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile

import io
import fitz
from PIL import Image
import os
import glob
PDFReader = download_loader("PDFReader")
import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from llama_index import download_loader
from xml.etree.ElementTree import Element, SubElement, tostring
import requests
import zipfile


from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()



def clear_images_folder():
    for file in os.listdir("images"):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            os.remove(os.path.join("images", file))

def clear_pages_folder():
    for file in os.listdir("pages"):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            os.remove(os.path.join("pages", file))


def update_json(topic_data):
    with open("output.json", "w") as f:
        st.session_state.toc = {"Topics": [{k: v} for k, v in topic_data.items()]}
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)


def load_db():
    if not os.path.exists("db.json"):
        with open("db.json", "w") as f:
            json.dump({}, f)
    
    with open("db.json", "r") as f:
        db = json.load(f)
    
    return db

def delete_chapter(chapter_name):
    db = load_db()
    if chapter_name in db:
        del db[chapter_name]
        with open("db.json", "w") as f:
            json.dump(db, f)
        return True
    return False

def post_xml_string(xml_string):
    url = 'https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourse'
    headers = {
        'Content-type': 'application/json'
    }
    payload = json.dumps({"ImportXML": str(xml_string)})
    response = requests.request("POST",url, headers=headers, data=payload)
    # print(data)
    print(response)
    return response


def json_to_xml(json_data, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets):
    chapter = Element('Chapter')

    no_of_bullets_element = SubElement(chapter, 'NoOfBullets')
    no_of_bullets_element.text = str(NoOfBullets)

    no_of_words_per_bullet_element = SubElement(chapter, 'NoOfWordsPerBullet')
    no_of_words_per_bullet_element.text = str(NoOfWordsPerBullet)

    no_of_words_for_vo_per_bullet_element = SubElement(chapter, 'NoOfWordsForVOPerBullet')
    no_of_words_for_vo_per_bullet_element.text = str(NoOfWordsForVOPerBullet)

    chapter_name_element = SubElement(chapter, 'ChapterName')
    chapter_name_element.text = chapter_name

    topics = SubElement(chapter, 'Topics')

    for topic_name, topic_info in json_data.items():
        topic = SubElement(topics, 'Topic')
        topic_name_element = SubElement(topic, 'TopicName')
        topic_name_element.text = topic_name

        # Add img tag for the topic if it exists
        if "img" in topic_info:
            for img_path in topic_info["img"]:
                img_element = SubElement(topic, 'img')
                img_element.text = img_path

        subtopics = SubElement(topic, 'SubTopics')
        for subtopic_info in topic_info['Subtopics']:
            subtopic = SubElement(subtopics, 'SubTopic')

            subtopic_name = SubElement(subtopic, 'SubTopicName')
            subtopic_name.text = subtopic_info['Subtopic']

            subtopic_content = SubElement(subtopic, 'SubTopicContent')
            subtopic_content.text = subtopic_info['content']

            # Add img tag for the subtopic if it exists
            if "img" in subtopic_info:
                for img_path in subtopic_info["img"]:
                    img_element = SubElement(subtopic, 'img')
                    img_element.text = img_path

    return tostring(chapter).decode()



def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1024))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.from_documents(documents,service_context=service_context)
    # st.session_state.index = index
    return index
        

######################       defining tabs      ##########################################

upload_col, refine_toc,  extract_col, miss_col, edit_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__","⚪ __missing_Contents__", "⚪ __Edit Contents__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])

if "toc" not in st.session_state:
    st.session_state.toc = {}




######################       Upload chapter column      ##########################################

uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")

forma = """"{
  "Topics": [
    {
      "Topic 1": [
        "Subtopic 1.1",
        "Subtopic 1.2",
        "Subtopic 1.3"
      ]
    },
    {
      "Topic 2": [
        "Subtopic 2.1",
        "Subtopic 2.2",
        "Subtopic 2.3"
      ]
    },
     continue with topics...
  ]
}

"""
if uploaded_file is not None:
        index = process_pdf(uploaded_file)
        if "index" not in st.session_state:
            st.session_state.index = index

        upload_col.success("Index created successfully")
        clear_images_folder()
        clear_pages_folder()
    # read PDF file
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # display PDF file
        with fitz.open(uploaded_file.name) as doc:
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save("pages/page-%i.png" % page.number) 
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


toc = upload_col.button("Genererate TOC")
try:
    if toc:
        toc_res = st.session_state.index.query(f" create a table of contents with topics and subtopics by reading through the document and create a table of contents that accurately reflects the main topics and subtopics covered in the document. The table of contents should be in the following format: " + str(forma))
        str_toc = str(toc_res)
        table_of_contents = json.loads(str_toc)

        if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents
        upload_col.write(st.session_state.table_of_contents)

        upload_col.success("TOC loaded, Go to the next tab")

except (KeyError, AttributeError) as e:
    print("Error generating TOC")
    print(f"Error: {type(e).__name__} - {e}")



######################       refining toc start      ##########################################


try:
    with refine_toc:
        column1, column2 = st.columns(2, gap="large")
        data = st.session_state.table_of_contents
        topic_data = {list(t.keys())[0]: list(t.values())[0] for t in data["Topics"]}
        if "topic_data" not in st.session_state:
            st.session_state['topic_data'] = topic_data
        column1.write("# Editor")

        column1.write("### Topics:")
        topic_name = column1.text_input("Enter New topic name:")

        if column1.button("Save New Topic"):
            if topic_name not in st.session_state['topic_data']:
                st.session_state['topic_data'][topic_name] = []
                update_json(topic_data)

        topic_options = list(st.session_state['topic_data'].keys())
        selected_topic = column1.selectbox("Select a Topic to edit Subtopics", topic_options)

        subtopics = st.session_state['topic_data'][selected_topic]

        column1.write("### Subtopics:")
        subtopics_input = column1.multiselect("Remove Unwanted Subtopics", subtopics, default=subtopics)

        if subtopics_input:
            st.session_state['topic_data'][selected_topic] = subtopics_input
            update_json(st.session_state['topic_data'])
        add = column1.button("Create New Subtopic")
        if "add" in st.session_state  or add:
            st.session_state['add'] = True
            new_subtopic = column1.text_input("Enter New Subtopic name:")
            if column1.button("Save New Subtopic"):
                if new_subtopic not in st.session_state['topic_data'][selected_topic]:
                    st.session_state['topic_data'][selected_topic].append(new_subtopic)
                    add= None
                    st.session_state['add'] = False
                    st.experimental_rerun()

        column2.write("# Table of Contents")

        for topic, subtopics in st.session_state['topic_data'].items():
            column2.markdown(f"**{topic}**")
            for subtopic in subtopics:
                column2.write(f"- {subtopic}")

        # if st.button("save total edits"):
        #     # st.session_state.table_of_contents = st.session_state['topic_data']
        #     st.success("TOC Edits Saved Successfully ")





except (KeyError, AttributeError) as e:
    print("Error refining toc")
    print(f"Error: {type(e).__name__} - {e}")





######################       extract content      ##########################################

try:
   

    if "new_dict" not in st.session_state:
            st.session_state.new_dict = {}
    for topic in st.session_state.toc["Topics"]:
        for key, value in topic.items():
            # Add a description for the topic
            st.session_state.new_dict[key] = {'content': '', 'Subtopics': []}
            # Add descriptions for the values
            for item in value:
                st.session_state.new_dict[key]['Subtopics'].append({'content': '', 'Subtopic': item})
    
    # extract_col.success("TOC formated correctly")
    

except (KeyError, AttributeError) as e:
    print("Error Formating TOC "+str(e))
    print(f"Error: {type(e).__name__} - {e}")



try:
    pagecol, ecol = extract_col.columns([2,5])
    quer = ecol.button("Extract Contents")

    
    # seca, secb = extract_col.columns(2)
    if quer:
        progress_bar = ecol.progress(0)
        total_items = sum(len(subtopics_dict['Subtopics']) for _, subtopics_dict in st.session_state.new_dict.items()) + len(st.session_state.new_dict)
        items_processed = 0
        for topic, subtopics_dict in st.session_state.new_dict.items():
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = index.query("extract the information about "+str(subtopic_name))
                subtopic_dict['content'] = subtopicres.response
                items_processed += 1
                progress_bar.progress(items_processed / total_items)
                ecol.info(f"Extracted {subtopic_name}")
            
            topicres = index.query("extract the information about "+str(topic))
            subtopics_dict['content'] = topicres.response
            items_processed += 1
            progress_bar.progress(items_processed / total_items)

        with open("newdict.json", "w") as f:

            json.dump(st.session_state.new_dict, f,indent=2)

    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = []
    
    pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    if pages_files:
        selected_page = pagecol.number_input("Change page number to compare:",step=1)
        selected_image = f"page-{selected_page}.png"
        # Display the selected image
        if selected_image:
            pagecol.image(os.path.join("pages", selected_image), use_column_width=True)
    else:
        pagecol.warning("No images found in the 'pages' folder.")

            # updated_json = json.dumps(st.session_state.new_dict, indent=2)
   

    # def update_json(topic_data):
       
    with open("newdict.json", "r") as f:
        st.session_state.new_dict = json.load(f)

        
    for topic_key, topic_value in st.session_state.new_dict.items():
        expander = ecol.expander(f"{topic_key}")
        expander.write(topic_value["content"])
        for subtopic in topic_value["Subtopics"]:
            expander.markdown(f"**{subtopic['Subtopic']}**")
            expander.write(subtopic["content"])


except (KeyError, AttributeError) as e:
    print("Error Extracting Data")
    print(f"Error: {type(e).__name__} - {e}")


######################       missing contents      ##########################################


try:

    amiscol, bmiscol = miss_col.columns([2,5])
    

    topic_names = [key for key, value in st.session_state.new_dict.items()]
    with open("newdict.json", "r") as f:
        sfword = json.load(f)
    new_query = bmiscol.text_input("Name of the missing Subtopic")
    topic_belong = bmiscol.selectbox("Select the belonging topic",topic_names)
    query_again = bmiscol.button("extract missing")
   
    if query_again:
   
        missing_info = index.query("extract the information about "+str(new_query))
      
        selected_topic = topic_belong
        new_subtopic = new_query
        content_value = missing_info.response
        topic_dict = sfword[selected_topic]
    # Append the new subtopic and its content to the appropriate topic
        topic_dict['Subtopics'].append({'content': content_value, 'Subtopic': new_subtopic})
        # bmiscol.write(sfword)

        with open("newdict.json", "w") as f:
            json.dump(sfword, f,indent=2)

        with open("newdict.json", "r") as f:
            st.session_state.sfword = json.load(f)

        for topic_key, topic_value in st.session_state.sfword.items():
            expander = bmiscol.expander(f"{topic_key}")
            expander.write(topic_value["content"])
            for subtopic in topic_value["Subtopics"]:
                expander.markdown(f"**{subtopic['Subtopic']}**")
                expander.write(subtopic["content"])
        
        with open("newdict.json", "w") as f:
            json.dump(st.session_state.sfword, f,indent=2)

    pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    if pages_files:
        selected_page = amiscol.number_input("compare with missing content:",step=1)
        selected_image = f"page-{selected_page}.png"
        # Display the selected image
        if selected_image:
            amiscol.image(os.path.join("pages", selected_image), use_column_width=True)
    else:
        amiscol.warning("No images found in the 'pages' folder.")


except (KeyError, AttributeError,FileNotFoundError) as e:
    print("Error missing Data")
    print(f"Error: {type(e).__name__} - {e}")


######################       edit contents      ##########################################

try:

    # if "new_dict" not in st.session_state:
    #     st.session_state.new_dict = new_dict

    with open("newdict.json", "r") as f:
        st.session_state.sfword = json.load(f)
        
    for topic, subtopics_dict in st.session_state.sfword.items():
        content = subtopics_dict['content']
        subtopics_dict['content'] = edit_col.text_area(f"Topic {topic}:", value=content)
        for subtopic_dict in subtopics_dict['Subtopics']:
            subtopic_name = subtopic_dict['Subtopic']
            content = subtopic_dict['content']
            subtopic_dict['content'] = edit_col.text_area(f"Subtopic {subtopic_name} under topic {topic} :", value=content)
    pass 

    if edit_col.button("Save"):
        edit_col.write(st.session_state.sfword)

except (KeyError, AttributeError) as e:
    print("Error saving Edited content")
    print(f"Error: {type(e).__name__} - {e}")




######################       export generated xml      ##########################################


try:
    # with 
    ondu, naduvan, rendu  = xml_col.columns([2,2,4])
    ondu.write("### Configure ")

    chapter_name = ondu.text_input("enter chapter name")
    NoOfBullets = ondu.text_input("No. of Bullets per Sub Topic")
    NoOfWordsPerBullet = ondu.text_input("No. of words per Bullet")
    NoOfWordsForVOPerBullet = ondu.text_input("No. of words for Voice Over per Bullet")
    save_xml = ondu.button("Save XML")
    
    naduvan.write("### Compare ")

    pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    if pages_files:
        selected_page = naduvan.number_input("Compare Images",step=1)
        selected_image = f"page-{selected_page}.png"
        # Display the selected image
        if selected_image:
            naduvan.image(os.path.join("pages", selected_image), use_column_width=True)
    else:
        naduvan.warning("No images found in the 'pages' folder.")


    rendu.write("### Select Images")

    left, right = rendu.columns([2,1])
    image_topic = left.selectbox("Select a topic", list(st.session_state.sfword.keys()),label_visibility="collapsed")
    add_to_topic = right.button("Add Image to Topic")

# Dropdown menu for selecting a subtopic based on the selected topic
    image_subtopic = left.selectbox("Select a subtopic", [subtopic["Subtopic"] for subtopic in st.session_state.sfword[image_topic]["Subtopics"]],label_visibility="collapsed")
    add_to_subtopic = right.button("Add image to Subtopic")

    image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    selected_images = []
    # for image in image_files:
    expander = rendu.expander("Select images")
    n_pages = 20

    image_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    page_index = rendu.number_input("Enter page number", min_value=1, max_value=n_pages, value=1)

    with rendu.expander(f"Page {page_index}", expanded=True):
        image_files = [f for f in os.listdir("images") if f.startswith(f'image_page{page_index}_') and f.endswith(tuple(image_exts))]
        if image_files:
            
            for image_filename in image_files:
                file_path = os.path.join("images", image_filename)
                if os.path.isfile(file_path):

                    rendu.image(file_path, caption=os.path.basename(file_path),width=150)
                else:
                    st.warning(f"Image not found: {os.path.basename(file_path)}")
        else:
            st.warning("No images found for this page.")
    
    selected_image = image_filename

    if add_to_topic:
        if "img" not in st.session_state.sfword[image_topic]:
            st.session_state.sfword[image_topic]["img"] = []
        st.session_state.sfword[image_topic]["img"].append(selected_image)
        rendu.success(f"Image {selected_image} added to topic {image_topic}")

    if add_to_subtopic:
        for subtopic in st.session_state.sfword[image_topic]["Subtopics"]:
            if subtopic["Subtopic"] == image_subtopic:
                if "img" not in subtopic:
                    subtopic["img"] = []
                subtopic["img"].append(selected_image)
                rendu.success(f"Image {selected_image} added to subtopic {image_subtopic}")
                break



    if save_xml:
        xml_output = json_to_xml(st.session_state.sfword, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets) 
        pretty_xml = minidom.parseString(xml_output).toprettyxml()

        db = load_db()
        db[chapter_name] = pretty_xml

        with open("db.json", "w") as f:
            json.dump(db, f)

        xml_file_path = os.path.join("images", f"{chapter_name}.xml")
        with open(xml_file_path, "w") as xml_file:
            xml_file.write(pretty_xml)
        # rendu.success(f"XML file saved as {xml_file_path}")

        with xml_col.expander("XML content"):
            xml_col.code(pretty_xml)

        # Zip the entire "images" folder with its contents
        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))

        zip_file_path = f"images/{chapter_name}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir("images", zipf)
        rendu.success(f"Zipped folder saved as {zip_file_path}")

        # st.session_state.table_of_contents = {}
        # st.session_state.selected_items = []
        # st.session_state.new_dict = {}
        # st.session_state.index = ""
        # st.session_state.sfword = {}
 
                
except (KeyError,NameError, AttributeError) as e:
    print("Error saving XML")
    print(f"Error: {type(e).__name__} - {e}")




######################      Manage XML      ##########################################

db = load_db()
chapter_list = list(db.keys())

if chapter_list:

    filesinsidefolder = manage_col.selectbox("Select a zip file", [f for f in os.listdir("images") if f.endswith(('.zip'))])

    if filesinsidefolder and filesinsidefolder.endswith('.zip'):
        file_path = os.path.join("images", filesinsidefolder)
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        manage_col.download_button(
            label="Download Zip File",
            data=file_bytes,
            file_name=filesinsidefolder,
            mime="application/zip",
        )
   
    else:
        manage_col.warning("No file selected.")



    selected_chapter = manage_col.selectbox("Select a chapter first:", chapter_list)
    delete_button = manage_col.button("Delete Chapter")
    post_button= manage_col.button("Continue with CourseBOT 2")


    if post_button:
        url = "https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourse"
        payload = json.dumps({
                                "ImportXML": str(db[selected_chapter])
                                })
        headers = {
                    'Content-Type': 'application/json'
                    }


        response = requests.request("POST", url, headers=headers, data=payload)
        st.write(response)
        print(response)
        response_dict = json.loads(response.text)

        url_to_launch = response_dict["result"]["urlToLaunch"]
        manage_col.subheader("Click on the url bellow to continue.")
        manage_col.write(url_to_launch)




    if delete_button:
        if delete_chapter(selected_chapter):
            manage_col.success(f"Chapter {selected_chapter} deleted successfully.")
            db = load_db()
            chapter_list = list(db.keys())
            if chapter_list:
                selected_chapter = manage_col.selectbox("Select a chapter:", chapter_list)
                manage_col.code(db[selected_chapter], language="xml")
            else:
                manage_col.warning("No chapters found. Upload a chapter and save its XML first.")
        else:
            manage_col.error(f"Failed to delete chapter {selected_chapter}.")

else:
    manage_col.warning("No chapters found. Upload a chapter and save its XML first.")

