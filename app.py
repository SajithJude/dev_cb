import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile

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


from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")
st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()


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

        subtopics = SubElement(topic, 'SubTopics')
        for subtopic_info in topic_info['Subtopics']:
            subtopic = SubElement(subtopics, 'SubTopic')

            subtopic_name = SubElement(subtopic, 'SubTopicName')
            subtopic_name.text = subtopic_info['Subtopic']

            subtopic_content = SubElement(subtopic, 'SubTopicContent')
            subtopic_content.text = subtopic_info['content']

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

upload_col, refine_toc,  extract_col, edit_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__", "⚪ __Edit Contents__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])

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
    
    extract_col.success("TOC formated correctly")
    

except (KeyError, AttributeError) as e:
    print("Error Formating TOC "+str(e))
    print(f"Error: {type(e).__name__} - {e}")



try:
    quer = extract_col.button("Extract Selected")
    seca, secb = extract_col.columns(2)
    if quer:
        progress_bar = extract_col.progress(0)
        total_items = sum(len(subtopics_dict['Subtopics']) for _, subtopics_dict in st.session_state.new_dict.items()) + len(st.session_state.new_dict)
        items_processed = 0
        for topic, subtopics_dict in st.session_state.new_dict.items():
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = index.query("extract the information about "+str(subtopic_name))
                subtopic_dict['content'] = subtopicres.response
                items_processed += 1
                progress_bar.progress(items_processed / total_items)
                extract_col.info(f"Extracted {subtopic_name}")
            
            topicres = index.query("extract the information about "+str(topic))
            subtopics_dict['content'] = topicres.response
            items_processed += 1
            progress_bar.progress(items_processed / total_items)


            updated_json = json.dumps(st.session_state.new_dict, indent=2)
        
    if "contents_list" not in st.session_state:
        st.session_state.contents_list = st.session_state.new_dict

    

except (KeyError, AttributeError) as e:
    st.info("Error Extracting Data")
    print(f"Error: {type(e).__name__} - {e}")


######################       Add missing contents      ##########################################


try:
                
    for topic_key, topic_value in st.session_state.contents_list.items():
        expander = seca.expander(f"{topic_key}")
        expander.write(topic_value["content"])
        for subtopic in topic_value["Subtopics"]:
            expander.markdown(f"**{subtopic['Subtopic']}**")
            expander.write(subtopic["content"])

    topic_names = [key for key, value in st.session_state.contents_list.items()]
    new_query = secb.text_input("Name of the missing Subtopic")
    topic_belong = secb.selectbox("Select the belonging topic",topic_names)
    query_again = secb.button("extract missing")

    if query_again:
        missing_info =  index.query("extract the information about "+str(new_query))
        selected_topic = topic_belong
        new_subtopic = new_query
        content_value = missing_info.response

        if new_subtopic not in st.session_state.contents_list[selected_topic]:
            st.session_state.contents_list[selected_topic][new_subtopic] = []

        st.session_state.contents_list[selected_topic][new_subtopic].append(content_value)
        # st.experimental_rerun()
        extract_col.write(st.session_state.contents_list)

except (KeyError, AttributeError) as e:
    st.info("Error addming missing Data")
    print(f"Error: {type(e).__name__} - {e}")







######################       edit contents      ##########################################

try:

    # if "new_dict" not in st.session_state:
    #     st.session_state.new_dict = new_dict
        
    for topic, subtopics_dict in st.session_state.new_dict.items():
        content = subtopics_dict['content']
        subtopics_dict['content'] = edit_col.text_area(f"Topic {topic}:", value=content)
        for subtopic_dict in subtopics_dict['Subtopics']:
            subtopic_name = subtopic_dict['Subtopic']
            content = subtopic_dict['content']
            subtopic_dict['content'] = edit_col.text_area(f"Subtopic {subtopic_name} under topic {topic} :", value=content)
    pass 

    if edit_col.button("Save"):
        edit_col.write(st.session_state.new_dict)

except (KeyError, AttributeError) as e:
    st.info("Error saving Edited content")
    print(f"Error: {type(e).__name__} - {e}")




######################       export generated xml      ##########################################


try:
    chapter_name = xml_col.text_input("enter chapter name")
    NoOfBullets = xml_col.text_input("No. of Bullets per Sub Topic")
    NoOfWordsPerBullet = xml_col.text_input("No. of words per Bullet")
    NoOfWordsForVOPerBullet = xml_col.text_input("No. of words for Voice Over per Bullet")

    save_xml = xml_col.button("Save XML")
    if save_xml:
        xml_output = json_to_xml(st.session_state.new_dict, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets) 
        pretty_xml = minidom.parseString(xml_output).toprettyxml()

        db = load_db()
        db[chapter_name] = pretty_xml

        with open("db.json", "w") as f:
            json.dump(db, f)

        with xml_col.expander("XML content"):
            xml_col.code(pretty_xml)

        st.session_state.table_of_contents = {}
        st.session_state.selected_items = []
        st.session_state.new_dict = {}
        st.session_state.index = ""
 
                
except (KeyError, AttributeError) as e:
    st.info("Error saving XML")
    print(f"Error: {type(e).__name__} - {e}")




######################      Manage XML      ##########################################

db = load_db()
chapter_list = list(db.keys())

if chapter_list:
    
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

