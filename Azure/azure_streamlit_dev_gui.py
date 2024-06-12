import streamlit as st

from AzureClasses import *


resource = st.sidebar.selectbox('Seleccion de recurso', ('Inicio', 'Key Vault'))



if resource == 'Key Vault':
    vault = VaultManager(keyVaultName='ControlCultivosKeyVault')
    st.write(vault.client.vault_url)
    
    vault.set_secret(secret_name='test', secret_value='test')
    
    st.write(vault.get_secret(secret_name='test'))


