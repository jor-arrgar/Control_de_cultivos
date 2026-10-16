import json 


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




def manage_previous_data():

    if 'file_data' not in st.session_state:
        st.session_state.file_data = None
    if 'loaded_data' not in st.session_state:
        st.session_state.loaded_data = False
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'file_loader' not in st.session_state:
        st.session_state.file_loader = 0

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
        c1.success(f"Archivo: {st.session_state.file_name}")
        if c2.button('🗑️'):
            st.session_state.file_loader += 1
            st.session_state.loaded_data = False
            st.session_state.file_data = None
            st.session_state.file_name = None
            st.rerun()



def download_file_with_data():

    if st.session_state.get('file_data') not in [None, {}] and st.session_state.get('file_name'):
        file_data_json = json.dumps(st.session_state.file_data, indent=5, sort_keys=True)
        st.sidebar.download_button(label='Descargar datos',
                                   data=file_data_json,
                                   file_name=st.session_state.file_name+'.json',
                                   mime='application/json')

    else:
        st.sidebar.warning('No hay datos para descargar')