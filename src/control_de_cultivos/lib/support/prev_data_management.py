import json 
from typing import Literal
import requests
import os

import streamlit as st


# DEPRECATED
def read_previous_data():
    '''Check for previous data each time the code runs for any reason.
    - If data present: returns the data
    - If data not present:
        - Check for uploaded data, returns them if uploaded
        - If not uploaded data, launch warnings and displays button for start new exploitation, returns empty data'''
        
    
    try:
        saved_data = st.session_state.loaded_data
    except:
        saved_data = False

    st.write('saved', saved_data)

    if not saved_data:
        file = st.sidebar.file_uploader('Archivo temporal', type=['.json'])
        if file is not None:
            file_name = file.name.replace('.json', '')
        else:
            file_name = st.sidebar.text_input('Nombre de archivo')
            if not len(file_name) > 0:
                file_name = None
            else:
                st.session_state.file_name = file_name
    
    if saved_data:
        if 'file_name' in st.session_state:
            file_name = st.session_state.file_name
        else:
            file_name = st.sidebar.text_input('Nombre de archivo')
        
        return st.session_state.file_data, file_name

    

    if file is None:
        
        #st.warning(MayConv('Ningún archivo de explotación* disponible.').all_mayus(mayus=mayus_))
        
        if st.sidebar.button('Nueva explotación'):
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
        st.sidebar.error('No hay datos cargados')
        
        
        
    return file_data, file_name




def manage_previous_data(mode:Literal['local', 'cloud']='local'):

    
    if 'file_data' not in st.session_state:
        st.session_state.file_data = None
    if 'loaded_data' not in st.session_state:
        st.session_state.loaded_data = False
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'file_loader' not in st.session_state:
        st.session_state.file_loader = 0


    def local_file_management():
        if st.session_state.file_data is None or st.session_state.file_data == {}:


            uploaded_file = st.sidebar.file_uploader('Archivo temporal', type=['.json'], key=f'uploader {st.session_state.file_loader}')



        
        
            if uploaded_file is not None:
                file_data = json.load(uploaded_file)
                st.session_state.file_data = file_data
                st.session_state.loaded_data = True
                st.session_state.file_name = uploaded_file.name.replace('.json', '')

            new_file_name = st.sidebar.text_input('Nombre de archivo', disabled=uploaded_file is not None, 
                                                value=st.session_state.file_name if 'file_name' in st.session_state else None)
            st.session_state.file_name_to_save = new_file_name

            if uploaded_file is None:
                st.session_state.file_data = {}
                st.session_state.loaded_data = False
                st.session_state.file_name = new_file_name
                

            else:
                try:
                    st.session_state.file_data = json.load(uploaded_file)
                except:
                    st.rerun()
                st.session_state.loaded_data = True
                st.session_state.file_name = uploaded_file.name.replace('.json', '')

        else:
            c1, c2 = st.sidebar.columns((2,1))
            c1.success(f"Archivo {mode}: {st.session_state.file_name}")
            if c2.button('🗑️'):
                st.session_state.file_loader += 1
                st.session_state.loaded_data = False
                st.session_state.file_data = None
                st.session_state.file_name = None
                st.rerun()


    def cloud_file_management():
        user = 'test'
        userKey = 'test123'

        FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001/")

        try:
            response = requests.get(FASTAPI_URL+"proxy/user_data/explotations", params={"user": user, "userKey": userKey, "check": 0})
            exploitations = response.json()
            #st.write(exploitations)
            if exploitations and len(exploitations) > 0:
                c1, c2 = st.sidebar.columns((4,1))
                selected_exploitation = c1.selectbox('Seleccione una explotación', exploitations)
                if selected_exploitation:
                    response = requests.get(FASTAPI_URL+"proxy/user_data/explotation", params={"user": user, "userKey": userKey, "explotation": selected_exploitation, "check": 0})
                    file_data = response.json()
                    if len(file_data) > 0:
                        c2.success('✅️')
                    else:
                        c2.error('❌️')
                        st.sidebar.warning("No se encontraron datos para la explotación seleccionada.")
                    st.session_state.file_data = file_data
                    st.session_state.loaded_data = True
                    st.session_state.file_name = selected_exploitation
                    uploaded_file = None
                else:
                    uploaded_file = None
            else:
                st.warning("No se encontraron explotaciones para el usuario.")
                uploaded_file = None

        except requests.exceptions.RequestException as e:
            st.error(f"Error al conectar con la API: {e}")
            exploitations = []
            uploaded_file = None
        except ValueError as e:
            st.error(f"Error al procesar la respuesta de la API: {e}")
            exploitations = []
            uploaded_file = None
        except KeyError as e:
            st.error(f"Error en la respuesta de la API: {e}")
            exploitations = []
            uploaded_file = None
        except json.JSONDecodeError as e:
            st.error(f"Error al decodificar la respuesta de la API: {e}")
            exploitations = []
            uploaded_file = None

        except Exception as e:
            st.error(f"Error al obtener la lista de explotaciones: {e}")
            exploitations = []
            uploaded_file = None


    if mode == 'local':
        local_file_management()
    elif mode == 'cloud':
        cloud_file_management()



def download_file_with_data():

    if st.session_state.get('file_data') not in [None, {}] and st.session_state.get('file_name'):
        file_data_json = json.dumps(st.session_state.file_data, indent=5, sort_keys=True)
        st.sidebar.download_button(label='Descargar datos',
                                   data=file_data_json,
                                   file_name=st.session_state.file_name+'.json',
                                   mime='application/json')

    else:
        st.sidebar.warning('No hay datos para descargar')