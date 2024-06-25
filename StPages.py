from st_pages import Page, add_page_title, show_pages

show_pages(
    [
        Page("Sobre Mim.py", "Sobre Mim", "🏠"),
        Page("Mapas.py", "Mapas", "🗺️"),
        Page(
            "Página - GEE - Download de Imagens.py", "Download de Imagens no GEE", "🌎"
        ),
        Page("Classificador_feijoes.py", "Feijões Estragados - Tensor Flow", "🫘"),
        Page(
            "Identificação de Pivôs - Interface.py", "Identificação de Círculos", "🔘"
        ),
        Page("Resumo_camarada.py", "Assistente financeiro (IA)", "👨‍💼"),
        Page("Poluicao_ar.py", "Poluição do Ar (OpenWeather)", "🌫️"),
        Page("Analise Descritiva de Dados.py", "Análise Descritiva de Dados", "📊"),
        Page("Dados NBA.py", "Previsão de Total Pontos NBA", "🏀"),
        Page("Trafego Pago.py", "Análise Dados Tráfego Pago (Looker)", "🧑‍💻"),
        Page("Incendios.py", "Dados de Queimadas (Power BI)", "🔥"),
    ]
)

add_page_title()  # Optional method to add title and icon to current page
