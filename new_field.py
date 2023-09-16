import streamlit as st
import pandas as pd
import numpy as np
import json
from time import sleep
from streamlit_modal import Modal

from functions import MayConv, traduce_booleans
    

def read_previous_data():
    '''Check for previous data each time the code runs for any reason.
    - If data present: returns the data
    - If data not present:
        - Check for uploaded data, returns them if uploaded
        - If not uploaded data, launch warnings and displays button for start new exploitation, returns empty data'''
        
    
    mayus_ = st.session_state.mayus_
    
    try:
        saved_data = st.session_state.loaded_data
    except:
        saved_data = False
        

    if not saved_data:
        file = st.sidebar.file_uploader(MayConv('Archivo temporal').all_mayus(mayus=mayus_), type=['.json'])
        if file is not None:
            file_name = file.name.replace('.json', '')
        else:
            file_name = st.sidebar.text_input(MayConv('Nombre de archivo').all_mayus(mayus=mayus_))
            if not len(file_name) > 0:
                file_name = None
    
    if saved_data:
        if 'file_name' in st.session_state:
            file_name = st.session_state.file_name
        else:
            file_name = st.sidebar.text_input(MayConv('Nombre de archivo').all_mayus(mayus=mayus_))
        return st.session_state.file_data, file_name

    

    if file is None:
        
        #st.warning(MayConv('Ningún archivo de explotación* disponible.').all_mayus(mayus=mayus_))
        
        if st.button(MayConv('Nueva explotación*').all_mayus(mayus=mayus_)):
            file_data = {}
            st.session_state.file_data = {}
            st.session_state.loaded_data = True
        else:
            if "loaded_data" not in st.session_state:
                file_data = {}
                st.session_state.file_data = {}
                st.session_state.loaded_data = False
            else:
                file_data = st.session_state.file_data
    else:
        file_data = json.load(file)
        st.session_state.file_data = file_data
        st.session_state.loaded_data = True
        
    if not st.session_state.loaded_data:
        #st.text(MayConv('* "explotación" como archivo de conjunto de parcelas, no como elemento de la PAC').all_mayus(mayus=mayus_))
        st.error(MayConv('No hay datos cargados').all_mayus(mayus=mayus_))
        
        
        
    return file_data, file_name
    
    

def new_field():
    '''Displays the GUI new field data input boxes, and returns the values as dict'''
    mayus_ = st.session_state.mayus_
    
    
    c1, c2 = st.columns((3, 2))
    field_name = c1.text_input(MayConv('Nombre de parcela').all_mayus(mayus=mayus_)).lower()
    field_surface = c2.number_input(MayConv('Superficie (hectareas)').all_mayus(mayus=mayus_))
    
    c1_, c2_, c3_, c4_, c5_ = st.columns((2, 1, 1, 1, 1))
    town = c1_.text_input(MayConv('Municipio').all_mayus(mayus=mayus_)).lower()
    poligono = c2_.number_input(MayConv('Polígono').all_mayus(mayus=mayus_), 0)
    parcela = c3_.number_input(MayConv('Parcela').all_mayus(mayus=mayus_), 0)
    
    c4_.write('·'*25); c5_.write('·'*25)
    pozo = c4_.checkbox(MayConv('Pozo').all_mayus(mayus=mayus_))
    rent = c5_.checkbox(MayConv('En renta').all_mayus(mayus=mayus_))
    
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
    mayus_ = st.session_state.mayus_
    
    field_name_ = MayConv('Nombre de parcela').all_mayus(mayus=mayus_)
    field_surface = MayConv('Superficie').all_mayus(mayus=mayus_)
    town = MayConv('Municipio').all_mayus(mayus=mayus_)
    poligono = MayConv('Polígono').all_mayus(mayus=mayus_)
    parcela = MayConv('Parcela').all_mayus(mayus=mayus_)
    pozo = MayConv('Pozo').all_mayus(mayus=mayus_)
    rent = MayConv('Renta').all_mayus(mayus=mayus_)
    
    columns_ = [field_name_, field_surface, town, poligono, parcela, pozo, rent]
    
    if not display and (new_field_info is not None):
        field_name = field_name_data
        info = new_field_info
        
    else:
        field_name = list(field_name_data.keys())[0]
        info = field_name_data[field_name]
    
    values = [MayConv(field_name).all_mayus(mayus=mayus_),
              info['superficie'],
              MayConv(info['localizacion']['municipio']).all_mayus(mayus=mayus_),
              info['localizacion']['poligono'],
              info['localizacion']['parcela'],
              traduce_booleans(info['pozo']),
              traduce_booleans(info['renta'])]
    
    df = pd.DataFrame(np.array([values]), columns=columns_)
    
    if display:
        st.table(df)
    else:
        return df
    

    
    
def check_for_existing_field(file_data, new_field):
    '''Checks for existing field in data based on town, "poligono" and "parcela". If true, returns "True" and 3\
elements needed later if updating is confirmed in another function. 

*That function MUST be outside this becouse I can't make the code fluildly working with the dialog box'''
    mayus_ = st.session_state.mayus_
    
    all_fields = display_all_fields(file_data, display=False)
    if all_fields is None:
        return False, None, None, None
    
    all_fields.reset_index(inplace=True)
    
    codes = list(zip(all_fields[MayConv('Municipio').all_mayus(mayus=mayus_)],
                    all_fields[MayConv('Polígono').all_mayus(mayus=mayus_)],
                    all_fields[MayConv('Parcela').all_mayus(mayus=mayus_)],
                     ))
    
    
    new_field_loc = tuple([str(val) for val in list(new_field.values())[0]['localizacion'].values()])
    

    if new_field_loc in codes:
        return True, codes, new_field_loc, all_fields
    
    else:
        return False, None, None, None
    

def update_entry_button(codes, new_field_loc, all_fields):
    '''Displays a warning and a button as confirmation of applying changes into one already existing field.
Returns the field name if confirmed, returns None if not.'''
    mayus_ = st.session_state.mayus_
    
    
    st.warning(MayConv('Esta parcela ya está incluída en los archivos, ¿quiere actualizarla?'))
    
    field_pos = codes.index(new_field_loc)
    field_name = all_fields['Nombre de parcela'][field_pos]


    if st.button(MayConv('Actualizar parcela').all_mayus(mayus=mayus_)):
        return field_name
    else:
        sleep(5)
        return None

    
    
def update_new_field(new_field, file_data):
    '''Checks for previous session state field name set (set by this function on a pre-run), and if a button is pressed,\
the new field is added to data. It also checks if the field is in the data, and launches a dialog box as confimation of\
rewriting. Returns the file data updated with the new/modify field'''
    mayus_ = st.session_state.mayus_
    
    if ('field_name') in st.session_state and (st.session_state.field_name != 'No name'):
        update = True
        field_name = st.session_state.field_name
        dialog_box = False
    else:
        dialog_box = True
      
    if not dialog_box or st.button(MayConv('Añadir parcela').all_mayus(mayus=mayus_)):
        
        update, codes, new_field_loc, all_fields = check_for_existing_field(file_data, new_field)
        if dialog_box and update:
            modal = Modal(key="Demo Key",title="test", padding=10, max_width=200)
            with modal.container():
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
        
        st.session_state.field_name = 'No name'
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
    

    

