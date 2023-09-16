import streamlit as st
from functions import MayConv
from streamlit_modal import Modal
from time import sleep


def delete_field(file_data):
    mayus_ = st.session_state.mayus_
    
    fields = list(file_data.keys())
    fields_to_remove = st.multiselect(MayConv('Parcelas para eliminar'), fields)
    
    if len(fields_to_remove) and st.button(MayConv('Eliminar parcelas').all_mayus(mayus=mayus_)):
        
        modal = Modal(key="Demo Key",title="test", padding=30, max_width=200)
        with modal.container():
            st.warning(MayConv('¿Eliminar las siguientes parcelas? ').all_mayus(mayus=mayus_))
            [st.write(field) for field in fields_to_remove]
            
            removed = False
            if st.button(MayConv('Eliminar').all_mayus(mayus=mayus_)):
                st.balloons()
                for field in fields_to_remove:
                    del file_data[field]
                removed = True
            else:
                sleep(5)
        st.session_state.loaded_data = True    
        return file_data , removed
    
    st.session_state.loaded_data = True
    return file_data, False