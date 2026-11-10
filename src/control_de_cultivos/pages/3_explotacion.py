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
from lib.support.prev_data_management import  manage_previous_data, download_file_with_data
from lib.support.functions import check_fastapi_status

# MARK: Page initialization
navigation_menu()
accesibility(show_strings=False)

working_fastapi = check_fastapi_status()
if not working_fastapi:
    st.warning("La API no está disponible. Algunas funciones pueden no funcionar correctamente.", icon="⚠️")
    manage_previous_data(mode='local')
else:
    st.success("La API está disponible.", icon="✅")
    manage_previous_data(mode='cloud')


# MARK: Page content
c1, c2 = st.columns((8, 2))
c1.title("Visor de explotación 🌾")
help_messages('visualizar explotación', c2)

file_data = st.session_state.get('file_data', None)


if file_data is not None and file_data != {}:
    tab1, tab2 = st.tabs(['Parcelas catastrales','Cultivos por temporada'])

    with tab1:
        fields_distributions(file_data)
        
    with tab2:
        crops_distribution(file_data)

else:
    st.warning('Cargue datos o genere una nueva explotación')

# MARK:DOWNLOAD FILE BUTTON
download_file_with_data()