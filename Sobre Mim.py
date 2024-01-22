import streamlit as st
from PIL import Image

# Barra Lateral
barra_lateral = st.sidebar.empty()

st.sidebar.markdown("- [Github](https://github.com/bsensix)")
st.sidebar.markdown("- [Mapas](https://www.spatialnode.net/bnunis)")
st.sidebar.markdown("- [Linkedin](https://www.linkedin.com/in/breno-nunes-b595781ba/)")
st.sidebar.markdown("- [E-mail](breno_1697@hotmail.com)")

st.title("🧑‍💻 Sobre Mim")
col1, col2 = st.columns(2)

col1.markdown("Bem-vindo ao meu **portfólio**! ")
col1.markdown(
    "Sou formado em Engenharia Ambiental pela (UFU) e atualmente trabalho como **Cientista de Dados**, especializado em análises de dados aplicados à **Agricultura e Meio Ambiente**. Além disso, sou um entusiasta de esportes e aplico algumas análises em esportes como Futebol e Basquete"
)
col1.markdown(
    "Este é um espaço onde você pode explorar alguns dos projetos nos quais estive envolvido. Sinta-se à vontade para entrar em contato caso tenha dúvidas."
)
col1.markdown(
    "Na aba à esquerda, você encontrará alguns desses projetos e um pouco da minha experiência."
)
col1.markdown("Atenciosamente, Breno Nunes")

image = Image.open(r"Dados/Perfil.png")
col2.image(image)

st.title("🛠️ Tecnologias e Ferramentas")

imagem1 = Image.open(r"Dados/Processamento Armazenamento.jpg")
st.image(imagem1)

st.title("📖 Artigos e Cursos")

with st.expander(
    "📝 Análise da Eficiência da Absorção de CO2 pelas plantas obtida por Sensores Remotos"
):
    st.write(
        "O estudo analisou a absorção de CO2 pela vegetação após um incêndio na Estação Ecológica do Panga em setembro de 2017, usando dados do satélite SENTINEL-2. Os resultados indicaram uma redução significativa na eficiência de sequestro de carbono pelas plantas após o incêndio, com uma relação inversamente proporcional entre os índices de vegetação dNBR e CO2flux. Em média, a absorção de CO2 pela vegetação diminuiu em 46% após incêndios de grande severidade."
    )
    st.write("https://repositorio.ufu.br/handle/123456789/34078")


with st.expander("📝 Correção Atmosférica de imagens do sensor WFI do CBERS-4"):
    st.write(
        "O Dark Object Subtraction é um método simples para corrigir efeitos atmosféricos de imagens de satélite. Quando se trabalha com cenas de satélites como Landsat, Sentinel, esta correção pode ser feita com softwares livres que em segundos normalizam a imagem. Porém, ainda nada semelhante em termos de softwares livres para este tipo de correção atmosférica foi desenvolvido para cenas dos                                                                                            Triângulo Mineiro/Alto Paranaíba. Uma delas foi corrigida pelo método, e outra não, focando no Índice de Vegetação por Diferença Normalizada, uma vez que ele sofre influência atmosférica. A aplicação das fórmulas e manipulação das imagens, considerando os valores da planilha online, foi feita com o software livre QGIS."
    )
    st.write(
        "https://proceedings.science/sbsr-2019/trabalhos/correcao-atmosferica-de-imagens-do-sensor-wfi-do-cbers-4-atraves-do-metodo-dark"
    )

with st.expander("📝 Zoneamento Ambiental da Bacia Hidrográfica do Rio Uberabinha"):
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

with st.expander("📓 Processamento de dados no QGIS para o Agro"):
    st.write(
        "Curso voltado a profissionais do Agro que querem trabalhar com dados georreferenciados"
    )
    st.write("https://conteudo.sensix.ag/qgis")

st.title("🎖️ Certificados")
with st.expander("Python"):
    link_name = "PYTHON BÁSICO AO AVANÇADO"
    link_url = (
        "https://www.udemy.com/certificate/UC-614d79cb-55dd-4576-b81f-f9f56d890a56/"
    )
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "ESTATÍSTICA COM PYTHON"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/estatistica-distribuicoes-e-medidas"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "PYTHON + PANDAS"
    link_url = (
        "https://cursos.alura.com.br/certificate/breno-1697/introducao-python-pandas"
    )
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "PYTHON + GEOPANDAS"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/geopandas-dados-geoespaciais"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "PYTHON + CLUSTERING"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/clustering-dados-sem-classificacao"
    st.markdown(f"[{link_name}]({link_url})")

with st.expander("Data Science e BI"):
    link_name = "ETL COM INTEGRATION SERVICES"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/business-intelligence-sql-server-e-integration-services"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "OLAP COM SQL SERVER"
    link_url = "https://cursos.alura.com.br/user/breno-1697/course/business-intelligence-olap-sql-server/certificate"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "DATA MESH"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/data-mesh-abordagem-distribuida-dados"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "DATA SCIENCE"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/data-science-primeiros-passos"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "BI"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/business-intelligence-introducao-inteligencia-empresarial"
    st.markdown(f"[{link_name}]({link_url})")

with st.expander("Power BI"):
    link_name = "POWER BI: ENTENDENDO AS FÓRMULAS DAX"
    link_url = (
        "https://cursos.alura.com.br/certificate/breno-1697/power-bi-formulas-dax"
    )
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "POWER BI: EXPLORANDO RECURSOS VISUAIS"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/power-bi-explorando-recursos-visuais"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "POWER BI DESKTOP"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/power-bi-desktop-primeiro-dashboard"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "POWER BI DESKTOP: TRATAMENTO DE DADOS NO POWER QUERY"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/power-bi-desktop-tratamento-dados-power-query"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "DASHBOARD COM POWER BI: VISUALIZANDO DADOS"
    link_url = (
        "https://cursos.alura.com.br/certificate/breno-1697/power-bi-visualizando-dados"
    )
    st.markdown(f"[{link_name}]({link_url})")


with st.expander("Machine Learning | Deep Learning | inteligência Artificial"):
    link_name = "Deep Learning com Tensor Flow"
    link_url = (
        "https://www.udemy.com/certificate/UC-e89a3b76-48d5-4b99-a2fa-296032e6b214/"
    )
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "Machine Learning - HIPERPARÂMETROS"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/machine-learning-otimizacao-de-modelos-atraves-de-hiperparametros"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "Machine Learning - EXPLORAÇÃO ALEATÓRIA"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/machine-learning-otimizacao-com-exploracao-aleatoria"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "Machine Learning - Validação de Dados"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/machine-learning-validando-modelos"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "Machine Learning - CLASSIFICAÇÃO POR TRÁS DOS PANOS"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/introducao-a-machine-learning-com-classificacao"
    st.markdown(f"[{link_name}]({link_url})")

    link_name = "Machine Learning - CLASSIFICAÇÃO COM SKLEARN"
    link_url = "https://cursos.alura.com.br/certificate/breno-1697/machine-learning-introducao-a-classificacao-com-sklearn"
    st.markdown(f"[{link_name}]({link_url})")
