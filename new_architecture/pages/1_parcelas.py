import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )



from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility
from lib.pages.p0_inicio.welcome_texts import help_messages
from lib.pages.p1_parcelas.new_field import new_field, display_new_field, update_new_field, display_all_fields
from lib.pages.p1_parcelas.delete_field import delete_field


navigation_menu()
accesibility(show_strings=False)

c1, c2 = st.columns((8, 2))
st.title("Gestión de parcelas 🚜")

file_data = st.session_state.get('file_data', None)
tab = st.segmented_control("Acción", ["Listado de parcelas", "Nueva parcela", "Eliminar parcela"],
                           default="Listado de parcelas", key="parcels_action_selector")

if tab == "Listado de parcelas":
    st.header("Listado de parcelas")
    display_all_fields(file_data)

elif tab == "Nueva parcela":
    st.header("Nueva parcela")
    help_messages('nueva parcela', c2)

    new_field_ = new_field()
    
    new_field_df = display_new_field(new_field_)
            
    file_data_ = update_new_field(new_field_, file_data, new_field_df)
    st.session_state.file_data = file_data_

elif tab == "Eliminar parcela":
    st.header("Eliminar parcela")
    help_messages('eliminar parcela', c2)

    file_data_, removed = delete_field(file_data)



