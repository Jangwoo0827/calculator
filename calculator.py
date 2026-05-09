import streamlit as st

st.set_page_config(page_title='calculator', layout="centered")

st.title("Calculator")

col1,col2 = st.columns(2)
with col1:
    a = st.number_input("A", value=0.0)
with col2:
    b = st.number_input("B", value=0.0)

op = st.selectbox("Calculation", ("Additon", "Subtraction", "Multiplication", "Division"))

if st.button("Calculation"):
    if op == "Additon":
        result = a + b
    elif op == "Subtraction":
        result = a - b
    elif op == "Multiplication":
        result = a * b
    else:
        if b == 0:
            st.warning("Can't divide with 0")
            st.stop()
        result = a / b

    st.success(f"결과: {result}")