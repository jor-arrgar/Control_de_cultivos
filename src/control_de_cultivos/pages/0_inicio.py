import streamlit as st
st.set_page_config(
    page_title="Control de cultivos",
    layout="wide",
    page_icon="🌱",
    )


from lib.support.pages_control import navigation_menu
from lib.support.accesibility import accesibility
from lib.support.prev_data_management import  read_previous_data, manage_previous_data, download_file_with_data

from lib.pages.p0_inicio.welcome_texts import welcome_message, help_messages


# MARK: Page initialization
navigation_menu()
accesibility(show_strings=False)
manage_previous_data()

# MARK: Page content
c1, c2 = st.columns((8, 2))
c1.title("Control de cultivos 🌱")
help_messages('inicio', c2)
welcome_message()


# MARK:DOWNLOAD FILE BUTTON
download_file_with_data()










# FILE DOWNLOAD
#if (file_name is not None) and (file_data is not None) and (file_name != ''): 
#    
#    # Check for incorrect crops
#    for field, data in file_data.items():
#        for season, crop_surface in data['temporadas'].items():
#            for crop, surface in tuple(crop_surface.items()):
#                if crop == '':
#                    file_data[field]['temporadas'][season].pop(crop, None)
#                    
#                    file_data[field]['temporadas'][season][None] = surface
#
#    # Check for all season keys as integers
#    for field, data in file_data.items():
#        for season, crop_surface in tuple(data['temporadas'].items()):
#            if type(season) == str:
#                file_data[field]['temporadas'].pop(season, None)
#                
#                file_data[field]['temporadas'][int(season)] = crop_surface
#
#
#    file_data_json = json.dumps(file_data, indent=5, sort_keys=True)
#    st.sidebar.download_button(label='Descargar datos',
#                       data=file_data_json,
#                       file_name=file_name+'.json',
#                       mime='application/json')
