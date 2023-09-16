import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from functions import MayConv, merge_by_field
from checkers import PAC_2023_2027
from new_field import read_previous_data

from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder


crop_list = ['Ajo', 'Barbecho', 'Barbecho semillado', 'Cebada', 'Centeno', 'Colza', 'Garbanzo', 'Girasol',
             'Guisante', 'Lenteja' , 'Maiz', 'Patata', 'Remolacha', 'Trigo', 'Triticale', '']

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
                except KeyError:
                    last_years = [None] + last_years
            
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
            
            selection = lambda x: list(x.keys()) if show is 'Cultivo' else list(x.values()) 
            filter_ = lambda x: selection(x) if x is not None else None
            
            new_file_data_lists.append([field,
                                        info['superficie'],
                                        MayConv(filter_(prev__prev_last_year_crop)).all_mayus(mayus=mayus_),
                                        MayConv(filter_(prev_last_year_crop)).all_mayus(mayus=mayus_),
                                        MayConv(filter_(last_year_crop)).all_mayus(mayus=mayus_),
                                       info['superficie']])
            
        else:
            new_file_data_lists.append([field, info['superficie'], None, None, None, info['superficie']])
            
        last_seasons_list = last_seasons.keys()   

        
        
    new_file_data_array = np.array(new_file_data_lists)
    
    print(last_years)
    new_file_data_df = pd.DataFrame(new_file_data_array, columns=['Parcela', 'Superficie',
                                                                  str(last_years[0]), str(last_years[1]), str(last_years[2]),
                                                                  'Dividir'])  
    
    
    # MOUNTING AG GRID WITH DIVISIONS COLUMN EDITABLE TO SET THE NUMBER OF DIVISIONS IN THE FIELD
    
    gd = GridOptionsBuilder.from_dataframe(new_file_data_df)
    
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(groupable=True)
    gd.configure_column('Parcela', editable=False)
    gd.configure_column('Superficie', editable=False)
    
    gd.configure_column('Dividir', editable=True, cellDataType='text')
    
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
    
    new_fields_list = []
    
    print(new_df)
    correct = True
    for  year_3, year_2, year_1,field, surface, divide in new_df.values:
        
        divisions = divide.replace(' ', '').split(',')
        
        
        for pos, div in enumerate(divisions):
            
            try:
                [float(val) for val in div if val != '.']
            except:
                st.warning(MayConv(f'Error => {field} ({div}) <=').all_mayus(mayus=mayus_))
                correct = False
                
            if correct:
                
                if len(divisions) > 1:
                    new_subfield_name = f'{field}_{pos+1}'
                else:
                    new_subfield_name = field
                    
                new_surface = float(div)
                
                print([new_subfield_name, new_surface, year_3, year_2, year_1])
                new_fields_list.append([new_subfield_name, new_surface, year_3, year_2, year_1])

    # RETURNING DATA
    
    if correct:
                    
        new_fields_df = pd.DataFrame(np.array(new_fields_list), columns=['Parcela', 'Superficie', str(last_years[0]), str(last_years[1]), str(last_years[2])])

        return new_fields_df
    
    else:
        
        st.error(MayConv('Compruebe los valores de división de parcelas. Deben cumplir con la estructura establecida.')\
            .all_mayus(mayus=mayus_))
        
        return None             
                

def set_crops(field_divisons_df):
    
    field_divisons_df['Cultivo'] = None
    
    gd_2 = GridOptionsBuilder.from_dataframe(field_divisons_df)
    
    gd_2.configure_pagination(enabled=True)
    gd_2.configure_default_column(groupable=True)
    gd_2.configure_column('Parcela', editable=False)
    gd_2.configure_column('Superficie', editable=False)

    gd_2.configure_column('Cultivo', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': crop_list })

    
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
    
    return df
            
            
            
def plot_crop_percents(percents):
    
    labels = list(percents.keys())
    values = list(percents.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_traces(textinfo='percent+label', pull=[0.1, 0, 0], hole=0.2)  # Example customization
    fig.update_layout(width=300 , height=300)
    
    st.sidebar.plotly_chart(fig)



def checker(fields_df):
    
    
    checker_ = PAC_2023_2027(fields_df)
    
    #crops, crops_percent, wrong_fields = checker_.return_info()    
    pac_check = checker_.check_proportions()
    
    error_message = PAC_2023_2027.translate_error(pac_check)
    
    plot_crop_percents(checker_.crops_percents)

    if pac_check == 0:
        return True
    
    else:
        if pac_check == 6:
            error_message = error_message + f'\n\nEn {checker_.wrong_crop_series}'
        st.error(error_message)
        return False
    

    
def check_for_bypasses(new_crops_df, year, file_data, check_):
    
    bypass, replace, not_assigned = True, True, True
    
    if not check_:
        bypass = st.checkbox('Permitir incumplir condiciones')
        
    for parcela in new_crops_df['Parcela']:
        if year in file_data[parcela.split('_')[0]]['temporadas'].keys():
            st.warning('Se va a reemplazar una entrada existente')
            replace = st.checkbox('Remplazar')
            break
    
    if any([crop == 'None' for crop in new_crops_df['Cultivo']]):
        st.warning('Parcelas sin asignar cultivos')
        not_assigned = st.checkbox('Continuar sin asignar')
        
    return replace, bypass, not_assigned

def add_new_season(file_data, merged_fields, year):
    
    new_file_data = file_data.copy()

    for field in merged_fields.keys():
        if 'temporadas' not in list(new_file_data[field].keys()):
            new_file_data[field].update({'temporadas':{}})
        new_file_data[field]['temporadas'].update({year:merged_fields[field]})
        
    return new_file_data





    
    
                
                