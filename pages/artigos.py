import streamlit as st

st.title("📖 Artigos e Cursos")

with st.expander(
    "📝Publicações: Análise da Eficiência da Absorção de CO2 pelas plantas obtida por Sensores Remotos"
):
    st.write(
        "O estudo analisou a absorção de CO2 pela vegetação após um incêndio na Estação Ecológica do Panga em setembro de 2017, usando dados do satélite SENTINEL-2. Os resultados indicaram uma redução significativa na eficiência de sequestro de carbono pelas plantas após o incêndio, com uma relação inversamente proporcional entre os índices de vegetação dNBR e CO2flux. Em média, a absorção de CO2 pela vegetação diminuiu em 46% após incêndios de grande severidade."
    )
    st.write("https://repositorio.ufu.br/handle/123456789/34078")


with st.expander(
    "📝Publicações: Correção Atmosférica de imagens do sensor WFI do CBERS-4"
):
    st.write(
        "O Dark Object Subtraction é um método simples para corrigir efeitos atmosféricos de imagens de satélite. Quando se trabalha com cenas de satélites como Landsat, Sentinel, esta correção pode ser feita com softwares livres que em segundos normalizam a imagem. Porém, ainda nada semelhante em termos de softwares livres para este tipo de correção atmosférica foi desenvolvido para cenas dos                                                                                            Triângulo Mineiro/Alto Paranaíba. Uma delas foi corrigida pelo método, e outra não, focando no Índice de Vegetação por Diferença Normalizada, uma vez que ele sofre influência atmosférica. A aplicação das fórmulas e manipulação das imagens, considerando os valores da planilha online, foi feita com o software livre QGIS."
    )
    st.write(
        "https://proceedings.science/sbsr-2019/trabalhos/correcao-atmosferica-de-imagens-do-sensor-wfi-do-cbers-4-atraves-do-metodo-dark"
    )

with st.expander(
    "📝Publicações: Zoneamento Ambiental da Bacia Hidrográfica do Rio Uberabinha"
):
    st.write(
        "Elaboração dos relatórios de Zoneamento Ambiental e Produtivo, da Bacia do Rio Uberabinha (ZAP) para o governo de Minas Gerais (SEMAD/ SEAPA -MG). (2019)"
    )
    st.write("- Relatório das Definições das Unidades de Paisagem")
    st.write("- Relatório do Estudo de Disponibilidade Hídrica")
    st.write(" - Relatório de Uso e Ocupação do Solo")
    st.write("https://drive.google.com/drive/folders/1DLwoMqBcDUUP0B8m7x-ufmdgUtGVE5wQ")
    st.write(
        "https://idesisema.meioambiente.mg.gov.br/geonetwork/srv/api/records/e3fb061a-3dfb-42b1-8e78-3b1a63599c21#:~:text=O%20Zoneamento%20Ambiental%20Produtivo%20(ZAP)%2C%20institu%C3%ADdo%20pelo%20Decreto%20Estadual,no%20estado%20de%20Minas%20Gerais"
    )

with st.expander("📓Curso: Processamento de dados no QGIS para o Agro"):
    st.write(
        "Curso voltado a profissionais do Agro que querem trabalhar com dados georreferenciados"
    )
    st.write("https://conteudo.sensix.ag/qgis")

with st.expander("📗 Ebook: Geração de Zonas de Manejo"):
    st.write("Ebook voltada para o processo de geração de Zonas de Manejo no Campo")
    st.write("https://conteudo.sensix.ag/ebook-zonas-de-manejo")

with st.expander("📰 Mapas de colheita"):
    st.write("Artigo sobre mapas de colheita: Mapas de colheita: como são gerados?")
    st.write("https://blog.sensix.ag/mapas-de-colheita-como-sao-gerados/")

with st.expander("📰 Amostragem de solos"):
    st.write(
        "Artigo sobre tipos de equipamentos para amostragem de solo: Tipos de equipamentos para fazer amostragem de solos"
    )
    st.write(
        "https://blog.sensix.ag/tipos-de-equipamentos-para-fazer-amostragem-de-solos/"
    )
with st.expander("📰 Sequestro de Carbono na Agricultura"):
    st.write("Artigo sobre: Sequestro de Carbono na Agricultura")
    st.write(
        "https://blog.sensix.ag/como-funciona-o-sequestro-de-carbono-na-agricultura/"
    )
with st.expander("📰 Agricultura Digital"):
    st.write("Artigo sobre: O que é Agricultura digital?")
    st.write("https://blog.sensix.ag/agricultura-digital-um-novo-comeco/")
