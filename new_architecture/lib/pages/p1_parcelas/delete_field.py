import streamlit as st

from time import sleep


def delete_field(file_data):
    
    fields = list(file_data.keys())
    fields_to_remove = st.multiselect('Parcelas para eliminar', fields)
    
    if len(fields_to_remove) and st.button('Eliminar parcelas'):
        
        modal = Modal(key="Demo Key",title="test", padding=30, max_width=200)
        with modal.container():
            st.warning('¿Eliminar las siguientes parcelas? ')
            [st.write(field) for field in fields_to_remove]
            
            removed = False
            if st.button('Eliminar'):
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