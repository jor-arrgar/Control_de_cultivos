import pandas as pd

import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )

from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility

from lib.pages.p0_inicio.welcome_texts import welcome_message, help_messages
from lib.pages.p2_temporadas.new_season import set_field_divisions, set_crops, field_exchange, checker, check_for_bypasses, add_new_season, display_fields_pop_up
from lib.support.functions import merge_by_field
from lib.support.prev_data_management import  manage_previous_data, download_file_with_data


# MARK: Page initialization
navigation_menu()
accesibility(show_strings=False)
manage_previous_data()


# MARK: Page content
c1, c2 = st.columns((8, 2))
c1.title("Temporadas de cultivo - Nueva temporada 🗓️")
help_messages('nueva temporada', c2)

file_data = st.session_state.get('file_data', None)

if file_data is not None and file_data != {}:
    c3, c4 = st.columns(2)
    year = c3.number_input('Año', 2000)
    #display_data(file_data)


    show = c4.selectbox('Mostrar en tabla', ('Cultivo', 'Superficie'))

    division_tab, crops_tab = st.tabs(['1. División de parcelas', '2. Asignación de cultivos a cada parcela/división'])

    with division_tab:
        field_divisions, last_years = set_field_divisions(file_data, show)

    with crops_tab:
        if field_divisions is not None:
            c1, c2 = st.columns((3, 1))
            c2.write('<p style=font-size:10px;color:red;font-weight:bold>Por alguna razón, si se quiere establecer \
                    un intercambio tiene que hacerse antes de cualquier cultivo</p>',
                        unsafe_allow_html=True)
            
            
            new_crops_df = set_crops(field_divisions, last_years)
            exchanged = field_exchange(new_crops_df)
            if exchanged is not None:
                exchanged_df = pd.DataFrame(exchanged)
            else:
                exchanged_df = None
            # función de checkeo de condiciones PAC

            check_ = checker(new_crops_df, exchanged_df)
            if check_ is not None:
                merged_fields = merge_by_field(new_crops_df)


                bypass, replace, not_assigned = check_for_bypasses(new_crops_df, year, file_data, check_)
                
                if st.sidebar.button('Relacion catastral'):
                    display_fields_pop_up(file_data)
                    
                #file_data_ = add_new_season(file_data, exchanged_df, merged_fields, year)
                #st.write(file_data_)
                if bypass and replace and not_assigned and st.button('Update'):
                    
                    file_data_ = add_new_season(file_data, exchanged_df, merged_fields, year)
                    st.write(file_data_)
                    st.session_state.file_data = file_data_
                #st.experimental_rerun()

else:
    st.warning('Cargue datos o genere una nueva explotación')

        

# MARK:DOWNLOAD FILE BUTTON
download_file_with_data()
