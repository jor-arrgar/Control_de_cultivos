import json 


import streamlit as st


#@st.cache_data(ttl=60*60*1, show_spinner="Cargando datos de archivo temporal...", scope="session")
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

    if not saved_data:
        file = st.sidebar.file_uploader('Archivo temporal', type=['.json'])
        if file is not None:
            file_name = file.name.replace('.json', '')
        else:
            file_name = st.sidebar.text_input('Nombre de archivo')
            if not len(file_name) > 0:
                file_name = None
    
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



