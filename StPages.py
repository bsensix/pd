from st_pages import Page, Section, add_page_title, show_pages

show_pages(
    [
        Page("Sobre Mim.py", "Sobre Mim", "🏠"),
        Section(name="🛰️ Geoprocessamento"),
        Page("Mapas.py", "Mapas", "🗺️"),
        Page(
            "Página - GEE - Download de Imagens.py", "Download de Imagens no GEE", "🌎"
        ),
        Section(name="📷 Visão Computacional"),
        Page("Classificador_feijoes.py", "Feijões Estragados - Tensor Flow", "🫘"),
        Page(
            "Identificação de Pivôs - Interface.py",
            "Identificação de Círculos (OpenCV)",
            "🔘",
        ),
        Section(name="🎲 Análise de dados"),
        Page("Poluicao_ar.py", "Poluição do Ar (OpenWeather)", "🌫️"),
        Page("Analise Descritiva de Dados.py", "Análise Descritiva de Dados", "📊"),
        Page("Dados NBA.py", "Previsão de Total Pontos NBA", "🏀"),
        Section(name="📈 Dashboards"),
        Page("Trafego Pago.py", "Dados Tráfego Pago (Looker)", "🧑‍💻"),
        Page("Incendios.py", "Dados de Queimadas (Power BI)", "🔥"),
    ]
)

add_page_title()  # Optional method to add title and icon to current page
