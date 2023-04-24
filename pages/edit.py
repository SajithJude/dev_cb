import streamlit as st
import json

def update_json(topic_data):
    with open("output.json", "w") as f:
        st.session_state['table_of_contents'] = {"Topics": [{k: v} for k, v in topic_data.items()]}
        json.dump(st.session_state['table_of_contents'], f)

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

col2.write("## Updated JSON:")
col2.json(st.session_state['topic_data'])




