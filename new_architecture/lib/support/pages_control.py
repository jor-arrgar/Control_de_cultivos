import streamlit as st


def navigation_menu():
    with st.sidebar:
        #st.title("Control de cultivos 🌱")
        #st.warning("Gestión de parcelas")
        st.page_link("pages/0_inicio.py", label="Inicio", icon="🏠")
        st.page_link("pages/1_parcelas.py", label="Parcelas", icon="🚜")
        st.page_link("pages/2_temporadas.py", label="Temporadas", icon="📅")
        st.page_link("pages/3_explotacion.py", label="Explotación", icon="🌾")