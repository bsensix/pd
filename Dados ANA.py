import hydrobr
import pandas as pd
from streamlit_folium import folium_static
import streamlit as st
import folium

# Importar estações INMET
inmet = hydrobr.get_data.ANA.list_prec_stations()
df = pd.DataFrame(inmet)


# Páginas
tab1, tab2 = st.tabs(["Estações", "Mapa Interpolado"])
# Informações
tab1.markdown("Esse painel ilustra um pouco dos dados da biblioteca HydroBr, um pacote de dados meteorológicos brasileiros. "
              "Nesse pacote você pode visualizar a localização das estações meteorológicas da ANA e INMET e baixar os dados das estações. "
              )
tab1.markdown("Para baixar os dados, basta inserir o código da estação no script abaixo:")

code_string = """ import hydrobr
import pandas as pd
# Lista de códigos da estação
codigos_estacoes = ['00047000','00047003']
# Dados de Precipitação
dados_chuva = hydrobr.get_data.ANA.prec_data(codigos_estacoes)
# Dados de Vazão 
dados_vazão = hydrobr.get_data.ANA.flow_data () 
"""
tab1.markdown('Documentação completa:')
tab1.write('https://wallissoncarvalho.github.io/HydroBr/')
tab1.code(code_string, language="python")

# Barra Lateral
barra_lateral = st.sidebar.empty()

# Filtros
st.sidebar.title('Filtros:')

list_estados = df['State'].unique()
filter_estado = st.sidebar.multiselect('Selecione o Estado:', list_estados,['MINAS GERAIS', 'MATO GROSSO','SÃO PAULO'])

list_city = df['City'].unique()
filter_city = st.sidebar.multiselect('Selecione a Cidade', list_city)

list_orgao = df['Responsible'].unique()
filter_orgao = st.sidebar.multiselect('Selecione o Orgão da Estação:', list_orgao)


# Aplicar os filtros ao DataFrame
if not filter_estado and not filter_city and not filter_orgao and not station_code:
    filtered_df = df  # Se nenhum filtro estiver selecionado, mostrar todos os dados
else:
    filtered_df = df[
        (df['State'].isin(filter_estado)) |
        (df['City'].isin(filter_city)) |
        (df['Responsible'].isin(filter_orgao)) 
            ]

# Criar o mapa
def create_map():
    # Crie um mapa centrado em uma localização inicial
    map_center = [-15.7801, -47.9292]  # Latitude e Longitude do centro do Brasil
    mymap = folium.Map(location=map_center, zoom_start=4)

    # Itere sobre as linhas do DataFrame
    for index, row in filtered_df.iterrows():
        # Adicione um marcador para cada estação com pop-up e ícone baseado no tipo
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Name']} Código Estação: {row['Code']}",
            icon=folium.Icon(color='blue')
        ).add_to(mymap)

    return mymap

# Aplicativo Streamlit
def main():
    st.header("Mapa de Estações")

    # Crie e mostre o mapa usando folium_static
    folium_map = create_map()
    folium_static(folium_map)

if __name__ == "__main__":
    main()



