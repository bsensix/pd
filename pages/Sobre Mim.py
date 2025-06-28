import streamlit as st
from PIL import Image

# Configurações da página
st.set_page_config(
    page_title="Sobre Mim",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Layout das abas
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Sobre Mim",
        "Formação e Experiência",
        "Artigos e Cursos",
        "Certificados",
        "Contatos",
    ]
)


with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            """
        <div style="background-color:#f8fafc;padding:32px 24px 24px 24px;border-radius:16px;">
            <h1 style="font-size:2.5rem;font-weight:700;margin-bottom:0.5rem;">Bem-vindo ao meu portfólio!</h1>
            <p style="font-size:1.2rem;margin-bottom:1rem;">
                Sou <b>Breno Nunes</b>, Engenheiro Ambiental formado pela UFU e atuo como Cientista de Dados na Sensix. Tenho experiência sólida em projetos de análise de dados, machine learning, geoprocessamento e inteligência artificial, com foco em soluções para. <br><br>
                <span style="margin-left:10px;">🌾 Agricultura de Precisão</span>
                <span style="margin-left:10px;">🌱 Agronegócio</span>
                <span style="margin-left:10px;">🌍 Meio Ambiente</span>
                <span style="margin-left:10px;">💼 Negócios</span>
                <span style="margin-left:10px;">⚽ Esportes</span>
            </p>
            <br>
            <p style="font-size:1.2rem;margin-bottom:1rem;">
                Ao longo da minha trajetória, desenvolvi habilidades em manipulação e visualização de dados, modelagem preditiva, integração de dados geoespaciais e automação de processos analíticos. Trabalho com ferramentas como Python, Pandas, Scikit-learn, Streamlit, Power BI, QGIS, além de tecnologias de cloud e bancos de dados.
            </p>
            <p style="font-size:1.2rem;margin-top:1.5rem;">
                Explore as abas acima para conhecer meus projetos, experiências e certificações!
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        image = Image.open(r"Dados/imagem_perfil.png")
        st.image(image, width=335)

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Experiência Profissional**")
        st.markdown(
            "- Cientista de dados na [**SENSIX**](https://sensix.ag/) fev/24 a atual"
        )
        st.markdown(
            "- Analista de Geoprocessamento na [**SENSIX**](https://sensix.ag/) dez/21 a fev/24"
        )
        st.markdown(
            "- Estágio em qualidade na [**SENSIX**](https://sensix.ag/) dez/20 a dez/21"
        )
        st.markdown(
            "- Estágio em Agrimensura na [**FINOTTI**](https://www.google.com/search?q=finotti+agrimensura&oq=FINOOTII+AGR&gs_lcrp=EgZjaHJvbWUqCAgBEAAYDRgeMgYIABBFGDkyCAgBEAAYDRgeMggIAhAAGA0YHjIHCAMQABjvBTIKCAQQABiABBiiBDIKCAUQABiABBiiBDIKCAYQABiABBiiBDIHCAcQABjvBdIBCDUzNjZqMGo0qAIAsAIB&sourceid=chrome&ie=UTF-8) jan/20 a dez/20"
        )
        st.markdown(
            "- Estágio em Geoprocessamento na [**ANGÁ**](https://www.anga.org.br/) nov/18 a dez/19"
        )
    with col2:
        st.markdown("**Formação**")
        st.markdown(
            "- [Engenheiro Ambiental - UFU](https://www.sei.ufu.br/sei/modulos/pesquisa/md_pesq_documento_consulta_externa.php?9LibXMqGnN7gSpLFOOgUQFziRouBJ5VnVL5b7-UrE5RiIkZETqExhQiCaJZaBRPmQAPqWq-9Z88oayS8_ITedQy6xopRHM3TCpNKUeQDtutT6Yi7ryXoJnGqJ-1o_gfq)"
        )
        st.markdown(
            "- [Cientista de Dados - IBM Data Science](https://www.coursera.org/account/accomplishments/professional-cert/Y78F3BDMKH4C)"
        )

    with col3:
        st.markdown("**Tecnologias**")
        st.markdown(
            "- Python, Pandas, Numpy, Scikit-learn, Streamlit, Plotly, Matplotlib, Seaborn, GeoPandas, Folium, OpenCV, Tensorflow, GDAL"
        )
        st.markdown("- SQL, PostgreSQL, MongoDB, Snowflake, AWS, Azure")
        st.markdown("- QGIS, ArcGIS, Google Earth Engine")
        st.markdown("- Power BI, Tableau, Data Studio, Excel")
        st.markdown("- Git, Docker, Airflow, FastAPI, Langchain")

with tab3:
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
        st.write(
            "https://drive.google.com/drive/folders/1DLwoMqBcDUUP0B8m7x-ufmdgUtGVE5wQ"
        )
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

    with tab5:
        st.markdown("**Contatos**")
        st.markdown("- [Github](https://github.com/bsensix)")
        st.markdown("- [Linkedin](https://www.linkedin.com/in/breno-nunes-b595781ba/)")
        st.markdown("- [E-mail](mailto:breno_1697@hotmail.com)")

with tab4:
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
        link_url = "https://cursos.alura.com.br/certificate/breno-1697/introducao-python-pandas"
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
        link_url = "https://cursos.alura.com.br/certificate/breno-1697/power-bi-visualizando-dados"
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

    with st.expander("Data Science Professional Certificate | IBM"):
        link_name = "Certificate Data Science"
        link_url = "https://www.coursera.org/account/accomplishments/professional-cert/Y78F3BDMKH4C"
        st.markdown(f"[{link_name}]({link_url})")


# Rodapé
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
        padding: 5px;
    }
    </style>
    <div class="footer">
        <p>Atenciosamente, Breno Nunes</p>
    </div>
    """,
    unsafe_allow_html=True,
)
