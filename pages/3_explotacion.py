import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )


from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility

from lib.pages.p0_inicio.welcome_texts import welcome_message, help_messages
from lib.pages.p3_explotacion.displaing_explotitaion import fields_distributions, crops_distribution


navigation_menu()
accesibility(show_strings=False)

c1, c2 = st.columns((8, 2))
c1.title("Visor de explotación 🌾")
help_messages('visualizar explotación', c2)

file_data = st.session_state.get('file_data', None)



tab1, tab2 = st.tabs(['Parcelas catastrales','Cultivos por temporada'])

with tab1:
    fields_distributions(file_data)
    
with tab2:
    crops_distribution(file_data)
