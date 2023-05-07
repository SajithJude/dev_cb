import streamlit as st

import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse("./pages/Time Management.xml")

# Get the root element
root = tree.getroot()

# Define a recursive function to print the structure of the nodes
def print_node_structure(node, indent):
    # Print the tag name and attributes of the node
    st.write(f"{indent}<{node.tag} {node.attrib}>")

    # Recursively print the structure of the child nodes
    for child in node:
        print_node_structure(child, indent + "  ")

    st.write(f"{indent}</{node.tag}>")

# Call the function with the root element
print_node_structure(root, "")
