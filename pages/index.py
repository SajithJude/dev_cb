import streamlit as st


index = st.session_state.index

qw= st.text_input("Enter query")

but = st.button("send")


if but:
    res= index.query(qw)
    st.write(res)
    st.write(res.source_nodes)
    st.write(res.get_formatted_sources())

