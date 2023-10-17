import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from functions import MayConv
from new_field import display_all_fields


def group_by(df, groups_column, column_to_be_grouped, rent_column):
    
        # Group by town_column and sum surface_column
    merged_data = pd.DataFrame(df.groupby([groups_column, rent_column])[column_to_be_grouped].sum())
   
    # Reset the index and assign it to a new column called 'Town'
    merged_data.reset_index(inplace=True)
    merged_data.rename(columns={groups_column: groups_column}, inplace=True)
    
    return merged_data

def surface_by_town(fields_dataframe, town_column, rent_column, surface_column):
    mayus_ = st.session_state.mayus_
    
    
    # Merge by town
    st.subheader(MayConv('Por municipio'))
    fields_dataframe_own = fields_dataframe[fields_dataframe[rent_column]=='NO']
    fields_dataframe_rent = fields_dataframe[fields_dataframe[rent_column]=='SI']
    merged_surface_by_town_own = group_by(fields_dataframe_own, town_column, surface_column, rent_column)
    merged_surface_by_town_rent = group_by(fields_dataframe_rent, town_column, surface_column, rent_column)
    fig = go.Figure(data=[go.Bar(x=merged_surface_by_town_own[town_column],
                                 y=merged_surface_by_town_own[surface_column],
                                 name=MayConv('Propias').all_mayus(mayus=mayus_)),
                          go.Bar(x=merged_surface_by_town_rent[town_column],
                                 y=merged_surface_by_town_rent[surface_column],
                                 name=MayConv('En renta').all_mayus(mayus=mayus_)),
                          ])
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig)
    
    
    




def surface_by_poligono(fields_dataframe,  town_column, poligono_column, rent_column, surface_column):
    mayus_ = st.session_state.mayus_
    
    towns = list(set(fields_dataframe[MayConv('Municipio').all_mayus(mayus=mayus_)]))
    towns.sort()
    # Merge by "poligono"
    st.subheader(MayConv('Por municipio y polígono').all_mayus(mayus=mayus_))
    town = st.selectbox(MayConv('Municipio').all_mayus(mayus=mayus_), towns)
    town_dataframe = fields_dataframe[fields_dataframe[town_column]==town]
    
    town_dataframe_own = town_dataframe[town_dataframe[rent_column]=='NO']
    town_dataframe_rent = town_dataframe[town_dataframe[rent_column]=='SI']
    
    merged_surface_by_poligono_own = group_by(town_dataframe_own, poligono_column, surface_column, rent_column)
    merged_surface_by_poligono_rent = group_by(town_dataframe_rent, poligono_column, surface_column, rent_column)
    
    fig_2 = go.Figure(data=[go.Bar(x=merged_surface_by_poligono_own[poligono_column],
                                   y=merged_surface_by_poligono_own[surface_column],
                                   name=MayConv('Propias').all_mayus(mayus=mayus_)),
                            go.Bar(x=merged_surface_by_poligono_rent[poligono_column],
                                   y=merged_surface_by_poligono_rent[surface_column],
                                   name=MayConv('En renta').all_mayus(mayus=mayus_))
                            ])
    fig_2.update_layout(barmode='stack')
    st.plotly_chart(fig_2)
    

def display_all_field_crops(file_data):
    
    crop_data = []
    for field, info in file_data.items():
        
        if 'temporadas' in info.keys():
            years = info['temporadas'].keys()
            
            crops_and_surfaces = [info['temporadas'][year] for year in years]

            for year_dict, year in zip(crops_and_surfaces, years):
                
                for crop, surface in year_dict.items():
                    
                    crop_data.append([field, crop, surface, year])
            
        else:
            crop_data.append([field, None, None, None])


    crop_df = pd.DataFrame(np.array(crop_data), columns=['Parcela', 'Cultivo', 'Superficie', 'Año'])
    
    crop_df['Superficie'] = crop_df['Superficie'].astype('float16')
    
    return crop_df
        
            


    

def fields_distributions(file_data):
    mayus_ = st.session_state.mayus_
    
    
    fields_dataframe = display_all_fields(file_data, display=False)
    
    if fields_dataframe is not None:
        #merged_surface_by_town = pd.group_by(fields_dataframe)[MayConv('Municipio').all_mayus(mayus=mayus_)].sum()
        town_column = MayConv('Municipio').all_mayus(mayus=mayus_)
        surface_column = MayConv('Superficie').all_mayus(mayus=mayus_)
        poligono_column = MayConv('Polígono').all_mayus(mayus=mayus_)
        rent_column = MayConv('Renta').all_mayus(mayus=mayus_)

        fields_dataframe[surface_column] = fields_dataframe[surface_column].astype('float')

            
        
        surface_by_town(fields_dataframe, town_column, rent_column, surface_column)
        surface_by_poligono(fields_dataframe, town_column, poligono_column, rent_column, surface_column)
    else:
        st.warning('explotacion vacia')
        
        
def display_crops_by_season(crops_df):
    
    crops_by_season = crops_df.groupby(['Cultivo', 'Año']).sum()
    

    
    if st.checkbox('Agrupar cultivos'):
        groups = st.multiselect('Grupos de cultivos', ('Cereales', 'Leguminosas', 'Tubérculos', 'Mejorantes',
                                                       'Otras hortalizas', 'Barbecho', 'Añadir individual'))
        st.write(groups)
        st.error('Funcionalidad no operativa todavia')
        df_to_display = None
           
    else:
        df_to_display = crops_df
    
    if df_to_display is not None:
        if len(set(df_to_display['Año'])) > 10:
            max_ = 10
        else:
            max_ = None
        
        data = [go.Bar(name=year, x=df_to_display[df_to_display['Año'] == year]['Cultivo'],
                                y=df_to_display[df_to_display['Año'] == year]['Superficie']) \
                                    for year in sorted(list(set(df_to_display['Año'])))[:max_]]

        layout = dict(title='Superficie de cultivos por temporada',
                    xaxis = dict(title='Cultivo'),
                    yaxis= dict(title='Hectáreas'))
        
        fig = go.Figure(data=data, layout=layout)
        
        # Change the bar mode
        fig.update_layout(barmode='group')
        
        st.plotly_chart(fig)
    
def display_crops_by_field(crops_df):
    
    crops_by_field_count = crops_df.groupby(['Parcela', 'Cultivo']).count()
    
    if st.checkbox('Agrupar cultivos'):
        st.error('Funcionalidad no operativa todavia')
        df_to_display = None
    else:
        df_to_display = crops_by_field_count
        
    if df_to_display is not None:
        
        take_first = lambda x: x[0]    
        data = [go.Bar(name=field, x=df_to_display.loc[field].index,
                                y=df_to_display.loc[field]['Superficie']) \
                                    for field in sorted(list(set([take_first(x) for x in df_to_display.index])))]

        layout = dict(title='Superficie de cultivos por parcela',
                    xaxis = dict(title='Cultivo'),
                    yaxis= dict(title='Hectáreas'))
        
        fig = go.Figure(data=data, layout=layout)
        
        # Change the bar mode
        fig.update_layout(barmode='group')
        
        st.plotly_chart(fig)
    
def display_crops_by_crops(crops_df):

    crops_by_field_count = crops_df.groupby(['Cultivo', 'Año']).count()
    crops_by_field_sum = crops_df.groupby(['Cultivo', 'Año']).sum()
    
    
    
    if st.checkbox('Agrupar cultivos'):
        st.error('Funcionalidad no operativa todavia')
        df_to_display = None
        title = None; y_title = None
    else:
        df_to_display = crops_by_field_sum
        title = 'Superficie'; y_title = 'Hectáreas'
        if st.checkbox('Número de parcelas'):
            df_to_display = crops_by_field_count
            title= 'Parcelas' ; y_title = 'Número de parcelas'
    
    if df_to_display is not None:
        take_first = lambda x: x[0]    
        data = [go.Bar(name=field, x=df_to_display.loc[field].index,
                                y=df_to_display.loc[field]['Superficie']) \
                                    for field in sorted(list(set([take_first(x) for x in df_to_display.index])))]

        layout = dict(title=f'{title} de cultivos por temporada',
                    xaxis = dict(title='Cultivo'),
                    yaxis= dict(title=y_title))
        
        fig = go.Figure(data=data, layout=layout)
        
        # Change the bar mode
        fig.update_layout(barmode='group')
        
        st.plotly_chart(fig)
    
    
    
def crops_distribution(file_data):
    mayus_ = st.session_state.mayus_
    
    crops_df = display_all_field_crops(file_data)
    
    grouping = st.selectbox('Selección interactiva', ('Por temporada', 'Por parcela', 'Por cultivo'))
    
    grouping_dict = {'por temporada': display_crops_by_season,
                     'por parcela': display_crops_by_field,
                     'por cultivo': display_crops_by_crops}
    
    grouping_dict[grouping.lower()](crops_df)