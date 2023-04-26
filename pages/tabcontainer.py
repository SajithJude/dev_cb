
import streamlit as st


tab1_image = st.image("https://static.streamlit.io/examples/cat.jpg", width=50)
tab2_image = st.image("https://static.streamlit.io/examples/dog.jpg", width=50)
tab3_image = st.image("https://static.streamlit.io/examples/owl.jpg", width=50)



tabs = st.tab_container()

with tabs:
    tab1 = st.tab(label=tab1_image)
    tab2 = st.tab(label=tab2_image)
    tab3 = st.tab(label=tab3_image)



with tab1:

    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)



with tab2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)



with tab3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)