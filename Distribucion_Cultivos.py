import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import json
from time import sleep

import new_field as nf
import delete_field as delf

import displaing_explotitaion as de
import new_season as ns

import gis_elements as ge

from functions import MayConv, merge_by_field
from welcome_texts import welcome_message, help_messages




# Setting mayus letters
def set_mayus_letters(c):
    '''Sets the session state for the mayus letters in texts, using a checkbox as reference.\nReturns nothing.'''
    
    mayus_ = c.checkbox('MAYUSCULAS')
    
    st.session_state.mayus_ = mayus_



c1, c2 = st.sidebar.columns(2)
set_mayus_letters(c1)
mayus_ = st.session_state.mayus_


# MAIN MENU
menu = st.sidebar.selectbox(MayConv('Menu pricipal').all_mayus(mayus=mayus_),
                            (MayConv('Inicio').all_mayus(mayus=mayus_),
                             MayConv('Nueva parcela').all_mayus(mayus=mayus_),
                             MayConv('Eliminar parcela').all_mayus(mayus=mayus_),
                             MayConv('Nueva temporada').all_mayus(mayus=mayus_),
                             MayConv('Visualizar explotación').all_mayus(mayus=mayus_),
                             MayConv('Mapas').all_mayus(mayus=mayus_)))

if menu.lower() == 'inicio':
    
    st.title('Control de cultivos')
    welcome_message(mayus_=mayus_)
    

# Read previous data (loaded data)
file_data, file_name = nf.read_previous_data()


# Launching if data is loaded
if st.session_state.loaded_data:
        
# ADD NEW FIELD
    if menu.lower() == 'nueva parcela':
        help_messages(menu, c2, mayus_=mayus_)
        
        new_field = nf.new_field()

        nf.display_new_field(new_field)
        
        file_data_ = nf.update_new_field(new_field, file_data)
        st.session_state.file_data = file_data_
        
        st.write('----------')
        
        #if st.checkbox(MayConv('Mostrar todas las parcelas en explotación*').all_mayus(mayus=mayus_)):
        nf.display_all_fields(file_data_)
    
# REMOVE FIELD
    elif menu.lower() == 'eliminar parcela':
        help_messages(menu, c2, mayus_=mayus_)
        
        file_data_, removed = delf.delete_field(file_data)
    
# START NEW SEASON
    elif menu.lower() == 'nueva temporada':
        modal = help_messages(menu, c2, mayus_=mayus_)

        st.title(MayConv('Nueva temporada').all_mayus(mayus=mayus_))
                
        year = st.number_input('Año', 2000)
        #ns.display_data(file_data)
        st.subheader(MayConv('División de parcelas').all_mayus(mayus=mayus_))
        
        show = st.selectbox('Mostrar en tabla', ('Cultivo', 'Superficie'))
        
        if modal is None:
            field_divisions, last_years = ns.set_field_divisions(file_data, show)
            
            if field_divisions is not None:
                st.subheader(MayConv('Selección de cultivo').all_mayus(mayus=mayus_))
                
                
                new_crops_df = ns.set_crops(field_divisions, last_years)
                
                # función de checkeo de condiciones PAC

                check_ = ns.checker(new_crops_df)
                merged_fields = merge_by_field(new_crops_df)


                bypass, replace, not_assigned = ns.check_for_bypasses(new_crops_df, year, file_data, check_)
                
                if st.sidebar.button('Relacion catastral'):
                    ns.display_fields_pop_up(file_data)
                    
                if bypass and replace and not_assigned and st.button('Update'):
                    
                    file_data_ = ns.add_new_season(file_data, merged_fields, year)

                    st.session_state.file_data = file_data_
                    st.experimental_rerun()
                
        
    
# DATA VISUALIZATION
    elif menu.lower() == 'visualizar explotación':
        help_messages(menu, c2, mayus_=mayus_)
        
        tab_names = [MayConv(text).all_mayus(mayus=mayus_) for text in ['Parcelas catastrales',
                                                                        'Cultivos por temporada']]
        
        tab1, tab2 = st.tabs(tab_names)
        
        with tab1:
            de.fields_distributions(file_data)
            
        with tab2:
            de.crops_distribution(file_data)

        
    elif menu.lower() == 'mapas':
        
        st.header('mapas')
        data = ge.plot_map()
        
        st.write(data)

        

        
    
# FILE DOWNLOAD
if (file_name is not None) and (file_data is not None) and (file_name != ''): 
    
    # Check for incorrect crops
    for field, data in file_data.items():
        for season, crop_surface in data['temporadas'].items():
            for crop, surface in tuple(crop_surface.items()):
                if crop == '':
                    file_data[field]['temporadas'][season].pop(crop, None)
                    
                    file_data[field]['temporadas'][season][None] = surface

    # Check for all season keys as integers
    for field, data in file_data.items():
        for season, crop_surface in tuple(data['temporadas'].items()):
            if type(season) == str:
                file_data[field]['temporadas'].pop(season, None)
                
                file_data[field]['temporadas'][int(season)] = crop_surface


    file_data_json = json.dumps(file_data, indent=5, sort_keys=True)
    st.sidebar.download_button(label=MayConv('Descargar datos').all_mayus(mayus=mayus_),
                       data=file_data_json,
                       file_name=file_name+'.json',
                       mime='application/json')
