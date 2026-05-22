
import pandas as pd 
import numpy as np 
import streamlit as st
from PIL import Image


# In[7]:


st.title('Download de Imagens através da API do GEE')

code_string = """
import ee
import datetime
import geopandas as gpd
import os

# Autenticação da conta 
ee.Authenticate()

# Inicialize o Earth Engine
ee.Initialize()

# Carregue o shapefile usando geopandas
shapefile_path = 'Caminho do seu shapefile'  
shp = gpd.read_file(shapefile_path)

# Converte o SHP para o tipo de geometria GEE
aoi = ee.Geometry.Polygon(list(shp['geometry'].iloc[0].exterior.coords))

# Defina o período de interesse
start_date = '2022-06-01'
end_date = '2022-06-30'

# Crie um filtro de datas
date_filter = ee.Filter.date(start_date, end_date)

# Filtrar as imagens Sentinel-2 de acordo com a área de interesse e o filtro de datas
collection = (ee.ImageCollection('COPERNICUS/S2')
              .filterBounds(aoi)
              .filter(date_filter)
              .sort('CLOUDY_PIXEL_PERCENTAGE', False))

# Selecione uma imagem de acordo com sua preferência (Nesse caso, menos nuvens)
image = ee.Image(collection.first())

# Obtenha a data da imagem
image_date = ee.Date(image.get('system:time_start'))

# Data como string 
image_date_str = image_date.format('YYYY-MM-dd').getInfo()

# Selecione bandas de interesse
bands = ['B2', 'B3', 'B4']

# Recorte a imagem para a área de interesse
clipped_image = image.clip(aoi)

# Converta todas as bandas para o tipo de dados desejado (UInt16)
clipped_image = clipped_image.toUint16()

# Nome da Imagem (usando a data da imagem)
image_name = 'Imagem_Sentinel_' + image_date_str

# Exporte a imagem para o Google Drive, nome da pasta
output_folder = 'Pasta do Google Drive'

# Nome da Imagem
output_file = os.path.join(image_name)

# Exporte a imagem para o Google Drive
task = ee.batch.Export.image.toDrive(image=clipped_image,
                                     description='Sentinel2_Image',
                                     fileNamePrefix=output_file,
                                     scale=10,
                                     region=aoi,
                                     folder=output_folder)
task.start()
"""

st.markdown(" Este código faz uso da API do Google Earth Engine para automatizar o procedimento de busca, seleção e download de imagens do satélite Sentinel-2. Inicialmente, o código se inicia com a autenticação da conta no Earth Engine e a configuração do ambiente. Os principais inputs do código são o shapefile que estabelece a área de interesse (AOI) e o período de interesse  O script tem como objetivo escolher a imagem com a menor porcentagem de cobertura de nuvens dentro da área de interesse. A imagem selecionada passa por um processo de recorte para se ajustar à AOI, e as bandas de interesse são definidas. Posteriormente, a imagem é exportada para uma pasta específica no Google Drive, utilizando o nome da imagem juntamente com a data como identificação no nome do arquivo.")
st.markdown("Para entender melhor as funções e possibilidade do Google Earth Engine, acesse a documentação: ")
st.markdown('https://cloud.google.com/earth-engine?authuser=1&hl=pt-br')        
st.code(code_string, language="python")





