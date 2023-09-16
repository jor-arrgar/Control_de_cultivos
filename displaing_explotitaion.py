import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import pandas as pd

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
    

def fields_distributions(file_data):
    mayus_ = st.session_state.mayus_
    
    
    fields_dataframe = display_all_fields(file_data, display=False)
    
    #merged_surface_by_town = pd.group_by(fields_dataframe)[MayConv('Municipio').all_mayus(mayus=mayus_)].sum()
    town_column = MayConv('Municipio').all_mayus(mayus=mayus_)
    surface_column = MayConv('Superficie').all_mayus(mayus=mayus_)
    poligono_column = MayConv('Polígono').all_mayus(mayus=mayus_)
    rent_column = MayConv('Renta').all_mayus(mayus=mayus_)
    fields_dataframe[surface_column] = fields_dataframe[surface_column].astype('float')
    
    surface_by_town(fields_dataframe, town_column, rent_column, surface_column)
    surface_by_poligono(fields_dataframe, town_column, poligono_column, rent_column, surface_column)