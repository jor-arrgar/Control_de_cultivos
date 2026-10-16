import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )


def main():

    st.switch_page("pages/0_inicio.py")



if __name__ == "__main__":
    main()
