import streamlit as st
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile
import os
import openai 
from pathlib import Path

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()

def clear_all_json_files():
    """Clear all JSON files in all directories under the current working directory"""
    
    root_directory = os.path.abspath(os.getcwd())
    
    # Iterate over all files and directories under the root directory
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # Iterate over all files in the current directory
        for filename in filenames:
            # Check if the file has a .json extension
            if filename.endswith('.json'):
                # Open the JSON file, clear its contents, and save the empty file
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'w') as json_file:
                    json.dump({}, json_file)

def update_json(topic_data):
    with open("output.json", "w") as f:
        st.session_state.toc = {"Topics": [{k: v} for k, v in topic_data.items()]}
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)

def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1900))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
    index = index.as_query_engine()


    if "index" not in st.session_state:
        st.session_state.index = index
        # st.session_state.index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
        # query_engine = st.session_state.index.as_query_engine()

        # st.session_state.index = index
    return st.session_state.index

######################       defining tabs      ##########################################

upload_col, refine_toc,  extract_col, miss_col, edit_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__","⚪ __missing_Contents__", "⚪ __Edit Contents__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])

if "toc" not in st.session_state:
    st.session_state.toc = {}


######################       Upload chapter column      ##########################################

uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")
toc_option = upload_col.radio("Choose a method to provide TOC", ("Generate TOC", "Copy Paste TOC"))
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
        clear_all_json_files()

        st.session_state.index = process_pdf(uploaded_file)
        upload_col.success("Index created successfully")


if toc_option == "Generate TOC":
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


elif toc_option == "Copy Paste TOC":
    toc_input = upload_col.text_area("Paste your Table of contents:")

    if upload_col.button("Save TOC"):
        try:
            # table_of_contents = json.loads(toc_input)
            toc_res = st.session_state.index.query(f"convert the following table of contents into the specified JSON format\n"+ "Table of contents:\n"+ str(toc_input) + "\n JSON format:\n"+ str(forma))
            str_toc = str(toc_res)
            table_of_contents = json.loads(str_toc)

            upload_col.write(table_of_contents)

            if "table_of_contents" not in st.session_state:
                st.session_state.table_of_contents = table_of_contents
            upload_col.write(st.session_state.table_of_contents)

            upload_col.success("TOC loaded, Go to the next tab")

        except json.JSONDecodeError as e:
            upload_col.error("Invalid JSON format. Please check your input.")

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
        
        delete_topic = column1.button("Remove Selected Topic")
        if delete_topic:
            if selected_topic in st.session_state['topic_data']:
                del st.session_state['topic_data'][selected_topic]
                update_json(st.session_state['topic_data'])
                st.experimental_rerun()
                
                
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
        
        if column1.button("Save"):
            try:
                if "new_dict" not in st.session_state:
                        st.session_state.new_dict = {}
                for topic in st.session_state.toc["Topics"]:
                    for key, value in topic.items():
                        # Add a description for the topic
                        st.session_state.new_dict[key] = {'Topic_Summary': '', 'VoiceOver': '', 'Subtopics': []}
                        # Add descriptions for the values
                        for item in value:
                            st.session_state.new_dict[key]['Subtopics'].append({'VoiceOver': '', 'Subtopic': item})
            except (KeyError, AttributeError) as e:
                print("Error Formating TOC "+str(e))
                print(f"Error: {type(e).__name__} - {e}")

        column2.write("# Table of Contents")

        for topic, subtopics in st.session_state['topic_data'].items():
            column2.markdown(f"**{topic}**")
            for subtopic in subtopics:
                column2.write(f"- {subtopic}")




except (KeyError, AttributeError) as e:
    print("Error refining toc")
    print(f"Error: {type(e).__name__} - {e}")


######################       extract content      ##########################################

try:
    pagecol, ecol = extract_col.columns([2,5],gap="large")

    # Course Description
    course_description_limit = pagecol.number_input("Course Description Word Count Limit", value=30, min_value=1)

    # Course Description VoiceOver
    course_description_voiceover_limit = pagecol.number_input("Course Description VoiceOver Word Count Limit", value=50, min_value=1)

    # Topic Summary
    topic_summary_limit = pagecol.number_input("Topic Summary Word Count Limit", value=30, min_value=1)

    # Topic Summary VoiceOver
    topic_summary_voiceover_limit = pagecol.number_input("Topic Summary VoiceOver Word Count Limit", value=50, min_value=1)

    # Number of Bullets per Slide
    num_bullets_per_slide = pagecol.number_input("Number of Bullets per Slide", value=4, min_value=1)

    # Number of Words per Bullet
    num_words_bullet = pagecol.number_input("Number of Words per Bullet", value=20, min_value=1)

    # Bullet VoiceOver
    bullet_voiceover_limit = pagecol.number_input("Bullet VoiceOver Word Count Limit", value=50, min_value=1)

    # Paraphrasing Percentage Range
    paraphrasing_range = pagecol.slider("Paraphrasing % Range", min_value=25, max_value=35, value=(25, 35))

    coursename = ecol.text_input("Enter Course Name")
    quer = ecol.button("Extract Contents")

    if quer:
        coursdescription = st.session_state.index.query(f"Generate a course description in {course_description_limit} no of words")
        voiceover = st.session_state.index.query(f"Generate a voiceover in {course_description_voiceover_limit} no of words")

    ecol.write(coursdescription.response)
    ecol.write(voiceover.response)

    ecol.write(st.session_state.new_dict)

except (KeyError,NameError, FileNotFoundError,AttributeError) as e:
    print("Error Extracting Data")
    print(f"Error: {type(e).__name__} - {e}")