import streamlit as st
from datetime import datetime


from lib.support.classes import Form



class User(Form):

    # Main form (table) attributes
    table_name = '01_users'
    datetime_columns = []
    integer_columns = []
    float_columns = []
    allowed_empty_columns = []


    # Table columns
    code = None
    updatedDate = None
    createdDate = None
    email = None
    name = None
    province = None
    nExplotations = None

    blockedDate = None
    blockedReason = None

    dppSigned = None
    dppSignedDate = None


    # Table columns user names
    user_code = "Código"
    user_updatedDate = "Fecha de actualización"
    user_createdDate = "Fecha de creación"
    user_email = "Email"
    user_name = "Nombre de usuario"
    user_province = "Provincia"
    user_nExplotations = "Nº de explotaciones"

    user_blockedDate = "Fecha de bloqueo"
    user_blockedReason = "Razón de bloqueo"

    user_dppSigned = "PPD firmada"
    user_dppSignedDate = "Fecha de firma de PPD"


    # Controlled lists for widgets
    controlled_lists = {}


    def __init__(self, table_entry:dict|None = None, added_stkey = ""):
        super().__init__(table_entry, added_stkey)


    def _set_up_callbacks(self):

        self.callbacks = {}

        # Function 1
        # ...
        # self.callbacks.update({col_name:function})


    def form(self):


        c1, c2 = st.columns((3,2))
        # email
        self.new_email = c1.text_input(
            label = self.user_email,
            value= self.email if self.loaded else self.columns.get('email', {}).get('DefaultValue', None),
            type= 'email', 
            max_chars= int(self.columns.get('email', {}).get('DataTypeSize', 0)),

            on_change=self.callbacks.get('email'),
            disabled=False,

            key=self.st_key + '_email'
        )
        self.new_code = self.new_email


        # name
        self.new_name = c2.text_input(
            label= self.user_name,
            value = self.name if self.loaded else self.columns.get('name', {}).get('DefaultValue', None),
            type='default',
            max_chars= int(self.columns.get('name', {}).get('DataTypeSize', 0)),

            on_change=self.callbacks.get('name'),
            disabled=False,
            
            key=self.st_key + '_name'
        )



        c3, c4 = st.columns(2)
        # province
        default = self.province if self.loaded else self.columns.get('province', {}).get('DefaultValue', None)
        provinces = self.get_unique_values('province')
        self.new_province = c3.selectbox(
            label= self.user_province,
            options= provinces,
            index=self.none_indexer_unique_selection(default, provinces, 'province'),

            on_change=self.callbacks.get('province'),
            disabled=False,
            
            key=self.st_key + '_province'
        )
        if self.new_province == 'NUEVO':
            self.new_province = c4.text_input(
                label= self.user_province + " (nueva entrada)",
                value = None,
                type='default',
                max_chars= int(self.columns.get('province', {}).get('DataTypeSize', 0)),

                on_change=self.callbacks.get('province'),
                disabled=False,
                            
                key=self.st_key + '_province_new'
            )


        # DPP readed
        if 'dpp_readed' not in st.session_state:
            st.session_state.dpp_readed = False
        c5, c6 = st.columns((2, 3))
        if c5.button('Leer Polítca de Protección de Datos'):
            User.data_protection_policy()
            st.session_state.dpp_readed = True

        self.new_dppSigned = c6.checkbox(
            label= "Estoy de acuerdo con la Política de Protección de Datos del Usuario.",

            on_change=self.callbacks.get('ddpSigned'),
            disabled=not st.session_state.dpp_readed,
                                        
            key=self.st_key + '_dppSigned'
        )
        if self.new_dppSigned:
            self.new_dppSignedDate = datetime.today()
        else:
            self.new_dppSignedDate = None



    @st.dialog('Política de Protección de Datos del Usuario')
    @staticmethod
    def data_protection_policy():

        st.write('This is the data protection policy')