import streamlit as st 
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile



st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"
PDFReader = download_loader("PDFReader")
loader = PDFReader()


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

    if st.button("Save TOC"):
        try:
            # table_of_contents = json.loads(toc_input)
            toc_res = st.session_state.index.query(f"convert the following table of contents into the specified JSON format\n"+ "Table of contents:\n"+ str(toc_input) + "\n JSON format:\n"+ str(forma))
            str_toc = str(toc_res)
            table_of_contents = json.loads(str_toc)

            st.write(table_of_contents)

            if "table_of_contents" not in st.session_state:
                st.session_state.table_of_contents = table_of_contents
            upload_col.write(st.session_state.table_of_contents)

            upload_col.success("TOC loaded, Go to the next tab")

        except json.JSONDecodeError as e:
            upload_col.error("Invalid JSON format. Please check your input.")





######################       refining toc start      ##########################################
