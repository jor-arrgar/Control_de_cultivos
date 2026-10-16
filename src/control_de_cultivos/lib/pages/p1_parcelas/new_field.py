import streamlit as st
import pandas as pd
import numpy as np
import json
from time import sleep


from lib.support.functions import traduce_booleans
    
  

def new_field():
    '''Displays the GUI new field data input boxes, and returns the values as dict'''
    
    
    c1, c2 = st.columns((3, 2))
    field_name = c1.text_input('Nombre de parcela').lower()
    field_surface = c2.number_input('Superficie (hectareas)')
    
    c1_, c2_, c3_, c4_, c5_ = st.columns((2, 1, 1, 1, 1))
    town = c1_.text_input('Municipio').lower()
    poligono = c2_.number_input('Polígono', min_value=0)
    parcela = c3_.number_input('Parcela', min_value=0)
    
    c4_.write('·'*25); c5_.write('·'*25)
    pozo = c4_.segmented_control('select', ['Pozo'], label_visibility='collapsed', key='pozo_selector')
    pozo = True if pozo == 'Pozo' else False
    rent = c5_.segmented_control('select', ['En renta'], label_visibility='collapsed', key='rent_selector')
    rent = True if rent == 'En renta' else False
    
    new_field = {field_name: {'superficie':field_surface,
                          'localizacion':{'municipio':town,
                                          'poligono':poligono,
                                          'parcela':parcela},
                          'pozo':pozo,
                          'renta':rent}}
    
    return new_field


    

    
def display_new_field(field_name_data, new_field_info=None, display=True):
    '''Generates a dataframe with the new field values. Two modes:
    - display=True: displays the dataframe in the streamlit GUI. Returns nothing.
    - display=False: returns the dataframe'''
    
    field_name_ = 'Nombre de parcela'
    field_surface = 'Superficie'
    town = 'Municipio'
    poligono = 'Polígono'
    parcela = 'Parcela'
    pozo = 'Pozo'
    rent = 'Renta'
    
    columns_ = [field_name_, field_surface, town, poligono, parcela, pozo, rent]
    
    if not display and (new_field_info is not None):
        field_name = field_name_data
        info = new_field_info
        
        
    else:
        field_name = list(field_name_data.keys())[0]
        info = field_name_data[field_name]

    
    values = [field_name,
              info['superficie'],
              info['localizacion']['municipio'],
              info['localizacion']['poligono'],
              info['localizacion']['parcela'],
              traduce_booleans(info['pozo']),
              traduce_booleans(info['renta'])]


    df = pd.DataFrame(np.array([values]), columns=columns_)
    
    if display:
        st.table(df)
        
    
    return df
    

    
    
def check_for_existing_field(file_data, new_field):
    '''Checks for existing field in data based on town, "poligono" and "parcela". If true, returns "True" and 3\
elements needed later if updating is confirmed in another function. 

*That function MUST be outside this becouse I can't make the code fluildly working with the dialog box'''

    
    all_fields = display_all_fields(file_data, display=False)
    if all_fields is None:
        return False, None, None, None
    
    all_fields.reset_index(inplace=True)
    
    codes = list(zip(all_fields['Municipio'],
                    all_fields['Polígono'],
                    all_fields['Parcela']))
    
    new_field_loc = tuple([str(val) for val in list(new_field.values())[0]['localizacion'].values()])
    

    if new_field_loc in codes:
        return True, codes, new_field_loc, all_fields
    
    else:
        return False, None, None, None
    

def update_entry_button(codes, new_field_loc, all_fields):
    '''Displays a warning and a button as confirmation of applying changes into one already existing field.
Returns the field name if confirmed, returns None if not.'''

    
    
    st.warning('Esta parcela ya está incluída en los archivos, ¿quiere actualizarla?')
    
    field_pos = codes.index(new_field_loc)
    field_name = all_fields['Nombre de parcela'][field_pos]


    if st.button('Actualizar parcela'):
        return field_name
    else:
        sleep(5)
        return None

    
    
def update_new_field(new_field, file_data, new_field_df):
    '''Checks for previous session state field name set (set by this function on a pre-run), and if a button is pressed,\
the new field is added to data. It also checks if the field is in the data, and launches a dialog box as confimation of\
rewriting. Returns the file data updated with the new/modify field'''

    
    if ('field_name') in st.session_state and (st.session_state.field_name != 'No name'):
        update = True
        field_name = st.session_state.field_name
        dialog_box = False
    else:
        dialog_box = True

    non_ceros_str = any([new_field_df.iloc[0][col] == '0' for col in ['Polígono', 'Parcela']])
    non_ceros = any([new_field_df.iloc[0][col] == 0 for col in ['Superficie']])
    non_empty = any([new_field_df.iloc[0][col] == '' for col in ['Nombre de parcela', 'Municipio']])
    c1, c2 = st.columns((1, 3))
    if non_ceros_str or non_ceros or non_empty:
        c2.warning('Por favor, rellene todos los campos de la parcela')
        disable = True
    else:
        disable = False
    if not dialog_box or c1.button('Añadir parcela', disabled=disable):
        
        update, codes, new_field_loc, all_fields = check_for_existing_field(file_data, new_field)
        field_name = st.session_state.get('field_name', None)
  
        if dialog_box and update:
            #modal = Modal(key="Demo Key",title="test", padding=10, max_width=200)
            #with modal.container():

            @st.dialog("Actualizar parcela")
            def update_entry_button(codes, new_field_loc, all_fields):
                field_name = update_entry_button(codes, new_field_loc, all_fields)
                if update and (type(field_name)==str):
                    st.session_state.field_name = field_name
        
        if not update:
            file_data.update(new_field)
            
        elif update and (type(field_name)==str):
            
            file_data[field_name]['superficie'] = list(new_field.values())[0]['superficie']
            file_data[field_name]['localizacion'] = list(new_field.values())[0]['localizacion']
            file_data[field_name]['pozo'] = list(new_field.values())[0]['pozo']
            file_data[field_name]['renta'] = list(new_field.values())[0]['renta']
            
            new_name =  list(new_field.keys())[0]
            if field_name != new_name:
                file_data[new_name] = file_data[field_name]
                del file_data[field_name]
        
        #st.session_state.field_name = 'No name'
        return file_data
    
    return file_data
    
        
            
def display_all_fields(file_data, display=True):
    '''Generates the table with all fields in data. Two modes:
    - display=True: displays the table in streamlit GUI. Returns nothing
    - display=False: return the merged dataframe'''
    
    
    dataframes = [display_new_field(new_field_name, new_field_info, display=False)\
        for new_field_name, new_field_info in file_data.items()]
    try:
        all_fields = pd.concat(dataframes)
        if display:
            st.table(all_fields)
        else:
            return all_fields
    except:
        pass
    

    

