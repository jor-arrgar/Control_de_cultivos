import streamlit as st
import folium
from folium import plugins

from streamlit_folium import st_folium



def generate_map():
    map_ = folium.Map(location=[41.49332051518723, -4.187950302048569], control_scale=True)

    # Añadir imagen de satelite
    tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
        ).add_to(map_)
    
    # Control de capas
    folium.LayerControl().add_to(map_) 


    # Agregar el complemento Draw al mapa
    draw = plugins.Draw(export=True)  # export=True permite guardar las geometrías dibujadas
    map_.add_child(draw)

    # Agregar herramientas de medición
    measure_control = plugins.MeasureControl()
    map_.add_child(measure_control)
    
    return map_


def plot_map():
    
    map_ = generate_map()
    
    map_data = st_folium(map_, width=1000, height=800)
    
    return map_data
    