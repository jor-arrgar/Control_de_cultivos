import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )


from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility
from lib.support.prev_data_management import  read_previous_data

from lib.pages.p0_inicio.welcome_texts import welcome_message, help_messages



navigation_menu()
accesibility(show_strings=False)
file_data, file_name = read_previous_data()

c1, c2 = st.columns((8, 2))
c1.title("Control de cultivos 🌱")
help_messages('inicio', c2)
welcome_message()

