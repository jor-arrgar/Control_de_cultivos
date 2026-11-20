import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )

from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility

from lib.pages.p0_inicio.welcome_texts import welcome_message, help_messages
from lib.support.functions import check_fastapi_status
from lib.pages.p4_usuarios.register import User


navigation_menu()
accesibility(show_strings=False)

working_fastapi = check_fastapi_status()
if not working_fastapi:
    st.warning("La API no está disponible. La funcionalidad de almacenamiento en la nube no está disponible y por tanto el \
               control de usuarios, tampoco.", icon="⚠️")
    st.info("Puede trabajar con la aplicación cargando y descargando los archivos de explotación manualmente desde el resto de menús.", icon="ℹ️")
else:
    c1, c2 = st.columns((8, 2))
    c1.title("Registro de usuarios 👥")

    user = User()
    #user.display_form_info()
    user.form()