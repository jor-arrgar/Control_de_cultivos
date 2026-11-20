import os
import requests
import json
from typing import Literal


import streamlit as st
from azure.identity import DefaultAzureCredential

################################################################################################################
# MEMORY MANAGEMENT


# MARK: Singleton
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]



################################################################################################################

################################################################################################################
# GUI+DB MANAGEMENT

# MARK: Form
class Form():

    FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001")

    # Main form (table) attributes
    table_name = None
    datetime_columns = []
    integer_columns = []
    float_columns = []
    allowed_empty_columns = []

    columns = {}


    # Table columns
    code = None
    updatedDate = None
    createdDate = None


    # Table columns user names
    user_code = "Código"
    user_updatedDate = "Fecha de actualización"
    user_createdDate = "Fecha de creación"


    # State control attributes
    loaded = False
    st_key = table_name


    # Controlled lists for widgets
    controlled_lists = {}

    # On-change callbacks for widgets
    callbacks = {}


    # Predefined widgets ready to fast deploy. Do not set up manually!
    form_widgets = {}


    # Inheritance checks
    def inheritance_checker(self):
        if self.table_name is None:
            return False, 1

        elif self.form_widgets != {}:
            return False, 2

        return True, 0


    # Initialization
    def __init__(self, table_entry:dict|None=None, added_stkey:str=""):

        inherit_check, code = self.inheritance_checker()
        if not inherit_check:
            raise AttributeError(f"'Form' inherited class ('{self.__class__}') incorrectly coded (code= {code}).")
        if table_entry is not None:
            for key in table_entry.keys():
                setattr(self, key, table_entry[key])

            self.loaded = True

        self.st_key = f"{self.table_name}_{self.loaded}_{self.code}_{added_stkey}"

        self.table_properties = self._load_table_properties()


    def _load_table_properties(self):

        
        url = self.FASTAPI_URL + f"/proxy/generaldb/get_table_struct?table_name={self.table_name}"

        @st.cache_data(ttl=60*5)
        def get_data():
            return requests.get(url)
        response = get_data()

        try:
            columns = response.json()
            if isinstance(columns, dict):
                if columns.get('message') == 'HTTP error':
                    columns = []
                    st.error(f'Error al descargar las propiedades de tabla "{self.table_name}":')
                    st.write(response.json())
                else:
                    pass
            elif not isinstance(columns, list) or len(columns) == 0 or not isinstance(columns[0], dict):
                st.error(f'Error al descargar las propiedades de tabla "{self.table_name}": Result not "list" or len=0 or no "dict" in list')
                st.write(response.json())

        except Exception as e:
            columns = []
            st.error(f'Error al descargar las propiedades de tabla "{self.table_name}"')
            st.write(e)

        
        for column in columns:
            col_name = column['ColumnName']
            if col_name in ['id', 'createdDate', 'updatedDate']:
                continue

            self.columns.update({col_name:{}})
            self.columns[col_name].update({'DataType':column.get('DataType')})
            self.columns[col_name].update({'DataTypeSize':column.get('DataTypeSize')})
            self.columns[col_name].update({'MaxLengthBytes':column.get('MaxLengthBytes')})
            self.columns[col_name].update({'NumericPrecision':column.get('NumericPrecision')})
            self.columns[col_name].update({'NumericScale':column.get('NumericScale')})
            self.columns[col_name].update({'IsNullable':column.get('IsNullable')})
            self.columns[col_name].update({'IsRequired':column.get('IsRequired')})
            self.columns[col_name].update({'DefaultValue':column.get('DefaultValue')})
            self.columns[col_name].update({'Description':column.get('Description')})




    # Info displaying
    def display_form_info(self):

        @st.dialog(f'"{self.table_name}" form info')
        def display():

            hardcoded_data_tab, database_tab = st.tabs(['Hardcoded', 'Database (auto)'])

            with hardcoded_data_tab:

                st.markdown(f"**- Table:** {self.table_name}")

                st.markdown(f'**- User attributes name**:')
                _, c = st.columns((1,9))
                t = []
                for column in self.columns.keys():
                    t.append(f"- {column}: {getattr(self, f'user_{column}')}")# + "br"#"\n\n"
                c.markdown('\n\n'.join(t))

                st.markdown("**- Controlled lists:**")
                st.write(self.controlled_lists)

                st.markdown("**- Callbacks:**")
                st.write(self.callbacks)


            with database_tab:

                st.markdown(f"**Database config for:** {self.table_name}")
                st.write(self.columns)


        if st.button(f'Display "{self.table_name}" form class info'):
            display()


    def __str__(self):

        form_values = {getattr(self, f"user_{c}"):getattr(self, f"new_{c}", None) for c in self.columns.keys()}
        jsonified_string = json.dumps(form_values, indent=4, ensure_ascii=False).encode('utf8').decode('utf8')
        return str(jsonified_string)



    # GUI
    def form(self):

        raise AttributeError('Inherited class does not have a "form" method')

    def none_indexer_unique_selection(self, value:int|str, list_to_check:list, column:str) -> int|None:
        if value is None:
            return None

        elif value in list_to_check:
            return list_to_check.index(value)

        else:
            raise ValueError(f'Unique values check incorrect for {self.table_name}.{column}. Not located in list')


    # Database calls
    @st.cache_data(ttl=60*5)
    def get_unique_values(_self, column):

        url = _self.FASTAPI_URL + f"/proxy/generaldb/get_column_uniques?table_name={_self.table_name}&column_name={column}"
        response = requests.get(url)
        try:
            options = response.json()
            if not isinstance(options, list):
                options = []
                raise(f"Error when loading unique values for '{_self.table_name}.{column}': Result not 'list'")
            else:
                options.append('NUEVO')
        except Exception as e:
            options = []
            raise(f"Error when loading unique values for '{_self.table_name}.{column}': {e}")

        return options

    