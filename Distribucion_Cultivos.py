import streamlit as st
import pandas as pd
import json

import new_field as nf
import delete_field as delf

import displaing_explotitaion as de
import new_season as ns

from functions import MayConv, merge_by_field



# Setting mayus letters

def set_mayus_letters():
    '''Sets the session state for the mayus letters in texts, using a checkbox as reference.\nReturns nothing.'''
    
    mayus_ = st.sidebar.checkbox('MAYUSCULAS')
    
    st.session_state.mayus_ = mayus_
    
    
set_mayus_letters()
mayus_ = st.session_state.mayus_


# MAIN MENU
menu = st.sidebar.selectbox(MayConv('Menu pricipal').all_mayus(mayus=mayus_),
                            (MayConv('Nueva parcela').all_mayus(mayus=mayus_),
                             MayConv('Eliminar parcela').all_mayus(mayus=mayus_),
                             MayConv('Nueva temporada').all_mayus(mayus=mayus_),
                             MayConv('Visualizar explotación').all_mayus(mayus=mayus_),
                             MayConv('Tareas').all_mayus(mayus=mayus_)))


# Read previous data (loaded data)
file_data, file_name = nf.read_previous_data()


# Launching if data is loaded
if st.session_state.loaded_data:
    
# ADD NEW FIELD
    if menu.lower() == 'nueva parcela':
        
        new_field = nf.new_field()

        nf.display_new_field(new_field)
        
        file_data_ = nf.update_new_field(new_field, file_data)
        st.session_state.file_data = file_data_
        
        st.write('----------')
        
        #if st.checkbox(MayConv('Mostrar todas las parcelas en explotación*').all_mayus(mayus=mayus_)):
        nf.display_all_fields(file_data_)
    
# REMOVE FIELD
    elif menu.lower() == 'eliminar parcela':
        
        file_data_, removed = delf.delete_field(file_data)
    
# START NEW SEASON
    elif menu.lower() == 'nueva temporada':

        st.title(MayConv('Nueva temporada').all_mayus(mayus=mayus_))
        
        year = st.number_input('Año', 2000)
        #ns.display_data(file_data)
        st.subheader(MayConv('División de parcelas').all_mayus(mayus=mayus_))
        
        show = st.selectbox('Mostrar en tabla', ('Cultivo', 'Superficie'))
        
        field_divisions = ns.set_field_divisions(file_data, show)
        
        if field_divisions is not None:
            st.subheader(MayConv('Selección de cultivo').all_mayus(mayus=mayus_))
            
            
            new_crops_df = ns.set_crops(field_divisions)
            
            # función de checkeo de condiciones PAC

            check_ = ns.checker(new_crops_df)
            merged_fields = merge_by_field(new_crops_df)
            

            bypass, replace, not_assigned = ns.check_for_bypasses(new_crops_df, year, file_data, check_)
            
            if bypass and replace and not_assigned and st.button('Update'):
                
                file_data_ = ns.add_new_season(file_data, merged_fields, year)

                st.session_state.file_data = file_data_
                st.experimental_rerun()

    
# DATA VISUALIZATION
    elif menu.lower() == 'visualizar explotación':
        
        de.fields_distributions(file_data)
        
    elif menu.lower() == 'tareas':
        
        st.write('- limpiar muestra de cultivos años anteriores en tablas (tambien cuando None)')
        st.write('- textos de ayuda (presentacion y boton popup en sidebar)')
        st.write('- revisar todas las strings para incluirlas en "MayConv" -- a lo mejor puede cambiarse a una lambda')
        st.write('- interacción con todas las tablas y guardado directo (previa alerta y confirmación)')
        

        

        
    
# FILE DOWNLOAD
if (file_name is not None) and (file_data is not None): 
    file_data_json = json.dumps(file_data)
    st.sidebar.download_button(label=MayConv('Descargar datos').all_mayus(mayus=mayus_),
                       data=file_data_json,
                       file_name=file_name+'.json',
                       mime='application/json')
