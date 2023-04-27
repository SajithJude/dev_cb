import requests
import streamlit as st
import os 

url = "https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourseZip"




filesinsidefolder = st.selectbox("Select a zip file", [f for f in os.listdir("images") if f.endswith(('.zip'))])


if st.button("send")
payload = {}
files=[
  ('ImportZip',('Chapter5.zip',open(os.path.join("images", filesinsidefolder), 'rb'),'application/zip'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

st.write(response.text)