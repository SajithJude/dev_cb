import streamlit as st
import json

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

data = json.loads(json_data)
topic_data = {list(t.keys())[0]: list(t.values())[0] for t in data["Topics"]}

st.title("Topics and Subtopics Editor")

if st.button("Add Topic"):
    topic_name = st.text_input("Enter topic name:")
    if topic_name:
        topic_data[topic_name] = []

topic_options = list(topic_data.keys())
selected_topic = st.selectbox("Select a topic:", topic_options)

subtopics = topic_data[selected_topic]

st.write("## Subtopics:")
subtopics_input = st.multiselect("", subtopics, default=subtopics)

if st.button("Save Subtopics"):
    topic_data[selected_topic] = subtopics_input

if st.button("Add Subtopic"):
    new_subtopic = st.text_input("Enter subtopic name:")
    if new_subtopic:
        topic_data[selected_topic].append(new_subtopic)

with open("output.json", "w") as f:
    json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)

st.write("## Updated JSON:")
st.json({"Topics": [{k: v} for k, v in topic_data.items()]})
