from functions import MayConv
import streamlit as st

welcome_description = '''"Control de cultivos" es una aplicación web para la visualización y control del reparto de \
cultivos en una explotación agraria a lo largo de diferentes temporadas.\n

Incluye un comprobador de condiciones obligatorias de la PAC.'''


gui_description = '''La vista de la aplicación se divide en dos elementos:
- Pestaña lateral izquierda: contiene el menú principal, el botón de subida de archivo, el de descarga, botones de \
accesibilidad y gráficos según la opción seleccionada.
- Ventana principal: en ella se muestra el cuerpo principal de la aplicación. Es donde apareceran los elementos para \
añadir parcelas, dividirlas, establecer cultivos, gráficas, tablas...'''

main_menu_description = '''1. Selección de acción principal: Tras subir un archivo previamente generado, o crear uno desde \
el botón "Nueva explotación", se permite el uso de las siguiente funciones, seleccionadas desde el desplegable "Menu principal":

    - Inicio (abierta actualmente): descripción e instrucciones
    - Nueva parcela: incluir nuevas parcelas en la explotación
    - Eliminar parcela: elimina parcelas de la explotación
    - Nueva temporada: establecer los cultivos para una temporada concreta. Permite dividir las parcelas y actualizar \
temporadas que ya existían previamente
    - Visualizar explotación: gráficas interactivas para la visualización de los datos de la explotación, como reparto de \
parcelas y cultivos en diferentes localidades, polígonos, distribución de cultivos y otros'''

upload_button = '''2. Bontón con texto en inglés: Permite subir un archivo de explotación ya existente. Al pulsar en él, se \
abre una ventana de selección de archivo la memoria local. Solo pueden subirse archivos ".json"'''

download_button = '''3. Botón de descarga: para descargar el nuevo archivo de explotación, es necesario establecer un \
nombre para este en el campo de texto, y al pulsar "Enter", aparererá el botón de descarga del mismo. El archivo \
aparece en la carpeta "Descargas" (o "Downloads")'''

new_exp_button = '''4. Botón de nueva explotación: crear una nueva explotación desde cero, sin archivo previo'''

accesibility_buttons = '''4. Botones de ayuda:

    - MAYUSCULAS: botón para establecer todos los textos de la aplicación en letra mayúscula en caso de dificultad de lectura
    - Ayuda: Botón que abre una ventana pop-up con las instrucciones de la sección correspondiente'''


introduction = '''Cargar una explotación existente a través del botón de subida o iniciar desde cero con el botón de \
"Nueva explotación" en la pestaña lateral'''

new_field_instructions = '''Establecer el nombre, superficie, localidad, polígono, número de parcela y resto de datos \
que se solicitan en los campos de textos. Cuando esté todo correcto, pulsar el botón "Añadir parcela". Si la parcela ya \
presente en la explotación (comprobado a través de municipio, polígono y parcela), se abrirá una ventana para confirmar \
los nuevos datos.

Las parcelas guardadas* en la explotación aparecen en la tabla inferior.

Esta explotación puede descargarse para incluir más parcelas y temporadas en otra ocasión, o puede usarse directamente \
en la opción de "Nueva temporada".

*Guardadas en la sesión web, no en el archivo local'''

new_fields_warning = 'Recomendable descargar este archivo por si ocurriese algún error en la app que borrase los datos \
en memoria.'

delete_field_instructions = '''Para eliminar una o varias parcelas, abrir el desplegable y pulsar en todas las parcelas \
que se quiere eliminar. Una vez elegidas, pulsar en "Eliminar parcelas", confirmar y cerrar manualmente el pop-up. '''

dividing_instructions = '''Establecer el año al que asociar temporada, y posteriormente divida las parcelas como \
necesite. Para ello, pinche en el cuadro de "Dividir" de la primera tabla y escriba las divisiones siguiendo la \
siguiente estructura:\n
        S1, S2, S3         (10.34 => 5, 5.34)'''

dividing_warning = 'Los valores decimales se separan con puntos, para que las divisiones puedan separarse por comas. \
Los espacios dan igual'

new_crops_instructions = '''Una vez dividas las parcelas, seleccionar en la siguiente tabla la especie a cultivar, pinchando en los \
cuadros de la columna "Cultivo". En la pestaña lateral de la app se generará un gráfico circular interactivo con la \
distribución de los cultivos añadidos.'''

new_crops_warning ='Hay que pinchar sobre el nombre del cultivo para que se guarde. En caso de establecer todos y \
y que aparezca el mensaje de campos vacios, clicar sobre cualquiera de los nombre de las columnas de la tabla de cultivo.'


checker_error_messages = '''Al establecer los cultivos, pueden aparecer mensajes de aviso y error que se deben leer \
atentamente. Entre ellos se incluyen las comprobaciones de las condiciones obligatorias de la PAC y comprobaciones \
internas a nivel de modificación de datos existentes y campos vacios. Estas condiciones pueden saltarse, simplemente \
hay que marcar las casillas de confirmación. Una vez que se cumplen todas las condiciones (o se ha confirmado que se \
ignoren), aparece el botón de "Añadir temporada", que incluye la nueva temporada en los datos.

Cuando se hayan incluido las temporadas que se quiera, se establece un nombre para el archivo y se descarga para usarlo \
en un futuro en esta misma aplicación.

Las tablas son interactivas a nivel de la última columna y los nombre de columna, desde donde se pueden ordenar los \
elementos de la misma de mayor a menor y viceverse a conveniencia (pinchando sobre el cuadro gris). Además, también \
se puede seleccionar si lo que se muestra en la tabla de división son los cultivos anteriores o las divisiones de \
superficie realizadas a través de un desplegable.'''


visualization_structions = '''En la pestaña de visualización, se puede acceder a multiples gráficos interactivos con la \
información de la explotación. Se pueden seleccionar parámetros tanto desde despleglables y casillas como directamnte \
la gráfica. La idea es que estas gráficas ayuden a organizar las explotaciones y cultivos'''



def welcome_message(mayus_):
    
    st.header(MayConv('Descripción de la aplicación').all_mayus(mayus=mayus_))
    st.write(MayConv(welcome_description).all_mayus(mayus=mayus_))
    st.write(MayConv(gui_description).all_mayus(mayus=mayus_))
    
    st.header(MayConv('Barra lateral izquierda').all_mayus(mayus=mayus_))
    st.write(MayConv(main_menu_description).all_mayus(mayus=mayus_))
    st.write(MayConv(upload_button).all_mayus(mayus=mayus_))
    st.write(MayConv(download_button).all_mayus(mayus=mayus_))
    st.write(MayConv(new_exp_button).all_mayus(mayus=mayus_))
    st.write(MayConv(accesibility_buttons).all_mayus(mayus=mayus_))
    
    st.header(MayConv('Instruccines de uso').all_mayus(mayus=mayus_))
    st.write(MayConv(introduction).all_mayus(mayus=mayus_))
    
    st.subheader(MayConv('Añadir parcela').all_mayus(mayus=mayus_))
    st.write(MayConv(new_field_instructions).all_mayus(mayus=mayus_))
    st.warning(MayConv(new_fields_warning).all_mayus(mayus=mayus_))
    
    st.subheader(MayConv('Eliminar parcela').all_mayus(mayus=mayus_))
    st.write(MayConv(delete_field_instructions).all_mayus(mayus=mayus_))

    st.subheader(MayConv('Nueva temporada').all_mayus(mayus=mayus_))
    st.write(MayConv(dividing_instructions).all_mayus(mayus=mayus_))
    st.warning(MayConv(dividing_warning).all_mayus(mayus=mayus_))
    st.write(MayConv(new_crops_instructions).all_mayus(mayus=mayus_))
    st.warning(MayConv(new_crops_warning).all_mayus(mayus=mayus_))
    
    st.header(MayConv('Visualización').all_mayus(mayus=mayus_))
    st.write(MayConv(visualization_structions).all_mayus(mayus=mayus_))
    
    