import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from functions import MayConv, merge_by_field
from checkers import PAC_2023_2027
from new_field import read_previous_data

from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import JsCode
from streamlit_modal import Modal


crop_list = ['Ajo', 'Barbecho', 'Barbecho semillado', 'Cebada', 'Centeno', 'Colza', 'Garbanzo', 'Girasol',
             'Guisante', 'Lenteja' , 'Maiz', 'Patata', 'Remolacha', 'Trigo', 'Triticale', None]

up_crops = ['Colza' , 'Garbanzo' , 'Girasol' , 'Guisante' , 'Lenteja']
leguminous_crops = ['Garbanzo' , 'Guisante' , 'Lenteja']

## https://medium.com/@nikolayryabykh/enhancing-your-streamlit-tables-with-aggrid-advanced-tips-and-tricks-250d4b57903

try:
    mayus_ = st.session_state.mayus_
except AttributeError:
    mayus_ = False
    


def display_data(data):
    st.write(data)
    

def check_for_past_seasons(field_info):
    
    if 'temporadas' in list(field_info.keys()):
        return field_info['temporadas']
    
    return {}


def display_fields_pop_up(file_data):
    
    modal = Modal(key="Datos catastrales",title="Datos catastrales", padding=10, max_width=600)
    with modal.container():
        
        st.write(" | ".join(['Nombre de parcela', 'Municipio', 'Poligono', 'Parcela']))
        for field, data in file_data.items():
            location = data['localizacion']
            st.write(field, "|", location['municipio'][:3], ',', location['poligono'], ' ', location['parcela'])
        
        
    

def set_field_divisions(file_data, show):
    
    show_keys = {'Cultivo': lambda x: x.keys(),
                 'Superficie': lambda x: x.values()}
    
    # SETTING DATAFRAME WITH PAST VALUES
    
    new_file_data_lists = []
    
    for field, info in file_data.items():
        
        last_seasons = check_for_past_seasons(info)
        
        if last_seasons != {}:
            
            
            last_years = list(last_seasons.keys())
            n_seasons = len(last_years)

            for year in range(3):
                try:
                    last_years[year]
                except IndexError:
                    last_years = [f'Sin establecer {year+1}'] + last_years
            
            last_year_crop = list(last_seasons.values())[-1]
            if n_seasons > 1:
                prev_last_year_crop = list(last_seasons.values())[-2]
                if n_seasons > 2:
                    prev__prev_last_year_crop = list(last_seasons.values())[-3]
                else:
                    prev__prev_last_year_crop = None
            else:
                prev__prev_last_year_crop = None
                prev_last_year_crop = None
            
            selection = lambda x: list(x.keys()) if show == 'Cultivo' else list(x.values()) 
            filter_ = lambda x: selection(x) if x is not None else None
            
            new_file_data_lists.append([field,
                                        info['superficie'],
                                        MayConv(filter_(prev__prev_last_year_crop)).all_mayus(mayus=mayus_),
                                        MayConv(filter_(prev_last_year_crop)).all_mayus(mayus=mayus_),
                                        MayConv(filter_(last_year_crop)).all_mayus(mayus=mayus_),
                                       info['superficie']])
            
        else:
            new_file_data_lists.append([field, info['superficie'], None, None, None, info['superficie']])
            last_years = ['Sin establecer 1', 'Sin establecer 2', 'Sin establecer 3']
        last_seasons_list = last_seasons.keys()   

        
        
    new_file_data_array = np.array(new_file_data_lists)
    
    new_file_data_df = pd.DataFrame(new_file_data_array, columns=['Parcela', 'Superficie',
                                                                  str(last_years[-3]), str(last_years[-2]), str(last_years[-1]),
                                                                  'Dividir'])  
    
    # MOUNTING AG GRID WITH DIVISIONS COLUMN EDITABLE TO SET THE NUMBER OF DIVISIONS IN THE FIELD
    
    gd = GridOptionsBuilder.from_dataframe(new_file_data_df)
    
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(groupable=True)
    gd.configure_column('Parcela', editable=False)
    gd.configure_column('Superficie', editable=False)
    gd.configure_column(str(last_years[-3]), editable=False)
    gd.configure_column(str(last_years[-2]), editable=False)
    gd.configure_column(str(last_years[-1]), editable=False)
    
    gd.configure_column('Dividir', editable=True, cellDataType='text')
    
    gd.configure_auto_height()
    
    gridOptions = gd.build()
    
    

    grid_table = AgGrid(new_file_data_df,
                        gridOptions=gridOptions,
                        fit_columns_on_grid_load=True,
                        height=250,
                        width='100%',
                        theme='streamlit',
                        update_mode=GridUpdateMode.GRID_CHANGED,
                        reload_data=False,
                        allow_unsafe_jscode=True,
                        editable=True)
    
    

    # CHECKING FOR DIVISION COLUMN VALUES INTEGRITY

    new_df = grid_table['data']
    
    new_df = new_df[['Parcela', 'Superficie', str(last_years[-3]), str(last_years[-2]), str(last_years[-1]), 'Dividir']]

    new_fields_list = []

    correct = True
    for  field, surface, year_3, year_2, year_1, divide in new_df.values:
        
        divisions = divide.replace(' ', '').split(',')
        
        
        for pos, div in enumerate(divisions):
            
            try:
                [float(val) for val in div if val != '.']
            except:
                st.warning(MayConv(f'Error => {field} ({div}) <=').all_mayus(mayus=mayus_))
                correct = False
                
            if correct:
                
                if len(divisions) > 1:
                
                    if pos > 27:
                        letter_pos = pos % 27 + 1
                    else:
                        letter_pos = pos + 1
                    
                    new_subfield_name = f'{field}-{chr(letter_pos+96)}'

                else:
                    new_subfield_name = field
                    
                new_surface = float(div)
                
                new_fields_list.append([new_subfield_name, new_surface, year_3, year_2, year_1])

    # RETURNING DATA
    
    if correct:
                    
        new_fields_df = pd.DataFrame(np.array(new_fields_list), columns=['Parcela', 'Superficie', str(last_years[-3]), str(last_years[-2]), str(last_years[-1])])
        
        return new_fields_df, last_years
    
    else:
        
        st.error(MayConv('Compruebe los valores de división de parcelas. Deben cumplir con la estructura establecida.')\
            .all_mayus(mayus=mayus_))
        
        return None, None   
                

def set_crops(field_divisons_df, last_years):
    
    
    field_divisons_df['Cultivo'] = None
    field_divisons_df['Intercambio'] = np.NaN
    
    
    gd_2 = GridOptionsBuilder.from_dataframe(field_divisons_df)
    
    gd_2.configure_pagination(enabled=True)
    gd_2.configure_default_column(groupable=True)
    gd_2.configure_column('Parcela', editable=False)
    gd_2.configure_column('Superficie', editable=False)

    
    
    checkbox_renderer = JsCode("""
                                class CheckboxRenderer{

                                    init(params) {
                                        this.params = params;

                                        this.eGui = document.createElement('input');
                                        this.eGui.type = 'checkbox';
                                        this.eGui.checked = params.value;

                                        this.checkedHandler = this.checkedHandler.bind(this);
                                        this.eGui.addEventListener('click', this.checkedHandler);
                                    }

                                    checkedHandler(e) {
                                        let checked = e.target.checked;
                                        let colId = this.params.column.colId;
                                        this.params.node.setDataValue(colId, checked);
                                    }

                                    getGui(params) {
                                        return this.eGui;
                                    }

                                    destroy(params) {
                                    this.eGui.removeEventListener('click', this.checkedHandler);
                                    }
                                }//end class
                                """)
    gd_2.configure_column('Intercambio', editable=True, cellEditor=checkbox_renderer)
    
    gd_2.configure_column('Cultivo', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': crop_list })

    gd_2.configure_auto_height()
    
    gridOptions = gd_2.build()
    

    grid_table_2 = AgGrid(field_divisons_df,
                        gridOptions=gridOptions,
                        fit_columns_on_grid_load=True,
                        height=250,
                        width='100%',
                        theme='streamlit',
                        update_mode=GridUpdateMode.GRID_CHANGED,
                        reload_data=False,
                        allow_unsafe_jscode=True,
                        editable=True)
    
    
    df = grid_table_2['data']

    df = df[['Parcela', 'Superficie', str(last_years[-3]), str(last_years[-2]), str(last_years[-1]), 'Cultivo', 'Intercambio']]
    df['Intercambio'].fillna(False, inplace=True)
    df['Intercambio'][df['Intercambio'] == 1]
    df['Intercambio'].replace(1, True)
    
    return df


def field_exchange(new_crops_df):
    
    exchanged = new_crops_df[new_crops_df['Intercambio'] == 1]
    values = []
    if len(exchanged) > 0:
        for field, tab in zip(exchanged.values, st.tabs(list(exchanged['Parcela']))):
            with tab:
                st.write('-- Indique la parcela y cultivo por el que se va a intercambiar')

                c1, c2, c3, c4, c5, c6 = st.columns((3, 1, 1, 3, 1,1))
                
                municipality = c1.text_input('Municipio', key=f'{field}_municipio')
                field_polygon = c2.number_input('Polígono', 0, key=f'{field}_poligono')
                field_number = c3.number_input('Parcela', 0, key=f'{field}_parcela')
                owner = c4.text_input('Dueño', key=f'{field}_dueño')
                crop = c5.selectbox('Cultivo',['']+ crop_list, key=f'{field}_cultivo')
                surface = c6.number_input('Superficie', min_value=0.00, value=float(field[1]), key=f'{field}_superficie')
                values.append({'municipio':municipality, 'poligono':field_polygon, 'parcela':field_number, 'dueño':owner, 'cultivo':crop, 'parcela original':field[0], 'superficie':surface})
        
        #st.table(pd.DataFrame(values))
        return values
    else:
        return None
            
               
            
def plot_crop_percents(percents):
    
    labels = list(percents.keys())
    values = list(percents.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_traces(textinfo='percent+label', pull=[0.1, 0, 0], hole=0.2)  # Example customization
    fig.update_layout(width=300 , height=300)
    
    st.sidebar.plotly_chart(fig)



def checker(fields_df, exchange_df):
    

    if exchange_df is None:
        st.write('-- No hay ningún intercambio de superficie')
        
    checker_ = PAC_2023_2027(fields_df, exchange_df)
    
    #crops, crops_percent, wrong_fields = checker_.return_info()    
    pac_check_conditionality = checker_.check_conditionality()
    if pac_check_conditionality != 0:
        st.error(f'INCOMPATIBILIDADES CON LA CONDICIONALIDAD:')
        for error in pac_check_conditionality:
            error_message_conditionality = PAC_2023_2027.error_code_translator(error)
            st.error(f'   --{error_message_conditionality[0]}: {error_message_conditionality[1]}')
    else:
        st.write('-- CONDICIONALIDAD "BCAM7" y "BCAM8" CORRECTAS')
            
    ecoregimen = st.number_input('Ecoregimen', min_value=3, max_value=5, value=3) # Hay del 1 al 8, pero a agricultura se aplican estos
    
    pac_check_ecoregimen = checker_.check_ecoregimen(ecoregimen)
    if pac_check_ecoregimen != 0:
        ecoregimen_name = PAC_2023_2027.error_code_translator(pac_check_ecoregimen[0])[0]
        st.error(f'INCOMPATIBILIDADES CON: {ecoregimen_name}')
        for error in pac_check_ecoregimen:
            error_message_ecoregimen = PAC_2023_2027.error_code_translator(error)
            st.error(f'   -- {error_message_ecoregimen[1]} - {error_message_ecoregimen[2]}')
    else:
        st.write(f'-- ECORREGIMEN "{checker_.eco345}" CORRECTO')

    
    st.sidebar.write('Hc totales: ', checker_.total_surface)
    st.sidebar.write('Hc barbecho minimo: ', checker_.barbecho_surface)
    plot_crop_percents(checker_.crops_percents)

    if pac_check_conditionality == 0 and pac_check_ecoregimen == 0:
        return True
    
    else:
        if pac_check_conditionality == 6:
            error_message = error_message + f'\n\nEn {checker_.wrong_crop_series}'
    
        return False
    

    
def check_for_bypasses(new_crops_df, year, file_data, check_):
    
    bypass, replace, not_assigned = True, True, True
    
    if not check_:
        bypass = st.checkbox('Permitir incumplir condiciones')
        
    for parcela in new_crops_df['Parcela']:

            
        if 'temporadas' not in file_data[parcela.split('-')[0]].keys():
            continue

        if year in file_data[parcela.split('-')[0]]['temporadas'].keys():
            st.warning('Se va a reemplazar una entrada existente')
            replace = st.checkbox('Remplazar')
            break

    if any([crop == 'None' for crop in new_crops_df['Cultivo']]):
        st.warning('Parcelas sin asignar cultivos')
        not_assigned = st.checkbox('Continuar sin asignar')
        
    return replace, bypass, not_assigned

def add_new_season(file_data, exchange_df, merged_fields, year):
    
    new_file_data = file_data.copy()

    
    for field in merged_fields.keys():
        if 'temporadas' not in list(new_file_data[field].keys()):
            new_file_data[field].update({'temporadas':{}})
        if 'temporadas intercambio' not in list(new_file_data[field].keys()):
            new_file_data[field].update({'temporadas intercambio':{}})
            
        if year in new_file_data[field]['temporadas'].keys():
            new_file_data[field]['temporadas'].pop(year, None)
        if year in new_file_data[field]['temporadas intercambio'].keys():
            new_file_data[field]['temporadas intercambio'].pop(year, None)
            
        new_file_data[field]['temporadas'].update({year:merged_fields[field]})
        if exchange_df is not None:
            if field in exchange_df['parcela original']:
                exchanged_field = list(exchange_df[exchange_df['parcela original']==field].values)
                exchanged_field.pop(-2)
                exchanged_keys = list(exchange_df.columns)
                exchanged_keys.pop(-2)
                
                exchanged_field_dict = {}
                [exchanged_field_dict.update({key, val}) for key, val in zip(exchanged_keys, exchanged_field)]
                new_file_data[field]['temporadas intercambio'].update({year:exchanged_field_dict})
            
        
    return new_file_data





    
    
                
                