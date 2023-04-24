import streamlit as st
import json

def update_json(topic_data):
    with open("output.json", "w") as f:
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)
    col2.write("## Updated JSON:")
    col2.json({"Topics": [{k: v} for k, v in topic_data.items()]})

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

col1.title("Topics and Subtopics Editor")

topic_name = col1.text_input("Enter New topic name to add:")

if col1.button("Add & New Topic"):
    if topic_name and topic_name not in topic_data:
        topic_data[topic_name] = []
        update_json(topic_data)

topic_options = list(topic_data.keys())
selected_topic = col1.selectbox("Select a topic:", topic_options)

subtopics = topic_data[selected_topic]

col1.write("## Subtopics:")
subtopics_input = col1.multiselect("", subtopics, default=subtopics)

if col1.button("Save Subtopics"):
    topic_data[selected_topic] = subtopics_input
    update_json(topic_data)

if col1.button("Add Subtopic"):
    new_subtopic = col1.text_input("Enter subtopic name:")
    if new_subtopic:
        topic_data[selected_topic].append(new_subtopic)
        update_json(topic_data)


