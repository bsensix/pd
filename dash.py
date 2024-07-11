import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# Leia os dados de automóveis em um dataframe pandas
df = pd.read_csv("path_to_your_file.csv")

# Crie o aplicativo Dash
app = Dash(__name__)

# Limpe o layout e não exiba exceções até que o callback seja executado
app.config.suppress_callback_exceptions = True

# Layout do aplicativo Dash
app.layout = html.Div(
    children=[
        html.H1(
            "Dashboard de Automóveis durante a Recessão", style={"textAlign": "center"}
        ),
        html.Div(
            [
                html.Label("Selecione o Tipo de Veículo:"),
                dcc.Dropdown(
                    id="vehicle-type-dropdown",
                    options=[
                        {"label": vt, "value": vt} for vt in df["Vehicle_Type"].unique()
                    ],
                    value=df["Vehicle_Type"].unique()[0],
                ),
            ],
            style={"padding": 10, "flex": 1},
        ),
        html.Div(
            [
                html.Label("Selecione o Ano:"),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[
                        {"label": year, "value": year} for year in df["Year"].unique()
                    ],
                    value=df["Year"].min(),
                ),
            ],
            style={"padding": 10, "flex": 1},
        ),
        html.Div(id="output-container", style={"padding": 10, "flex": 1}),
        html.Div(
            [
                dcc.Graph(id="recession-stats-graph"),
                dcc.Graph(id="annual-stats-graph"),
            ],
            style={"display": "flex", "flexDirection": "row"},
        ),
    ]
)


# Callback para atualizar o contêiner de saída e os gráficos
@app.callback(
    [
        Output("output-container", "children"),
        Output("recession-stats-graph", "figure"),
        Output("annual-stats-graph", "figure"),
    ],
    [Input("vehicle-type-dropdown", "value"), Input("year-dropdown", "value")],
)
def update_graphs(selected_vehicle_type, selected_year):
    # Filtrar os dados com base na seleção
    df_filtered = df[
        (df["Vehicle_Type"] == selected_vehicle_type) & (df["Year"] == selected_year)
    ]
    df_recession = df[
        (df["Recession"] == 1) & (df["Vehicle_Type"] == selected_vehicle_type)
    ]

    # Crie o gráfico de estatísticas de recessão
    recession_fig = px.line(
        df_recession,
        x="unemployment_rate",
        y="Automobile_Sales",
        title="Efeito da Taxa de Desemprego nas Vendas de Automóveis durante a Recessão",
        labels={
            "unemployment_rate": "Taxa de Desemprego",
            "Automobile_Sales": "Vendas de Automóveis",
        },
        color="Vehicle_Type",
    )

    # Crie o gráfico de estatísticas anuais
    annual_fig = px.line(
        df_filtered,
        x="Month",
        y="Automobile_Sales",
        title=f"Vendas de Automóveis em {selected_year} por Mês",
        labels={"Month": "Mês", "Automobile_Sales": "Vendas de Automóveis"},
        color="Vehicle_Type",
    )

    # Atualize o contêiner de saída
    output_text = f"Statísticas para o Tipo de Veículo: {selected_vehicle_type} no Ano: {selected_year}"

    return output_text, recession_fig, annual_fig


if __name__ == "__main__":
    app.run_server(debug=True)

input_year = ""
data=df
yas=df

elif (input_year and selected_statistics=='Yearly'):  # noqa: E999
    yearly_data = data[data['Year'] == input_year]
                              
# Plot 1: Yearly Automobile sales using line chart for the whole period.
yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
Y_chart1 = dcc.Graph(figure=px.line(yas,x='Year',y='Automobile_Sales',title='Yearly Automobile Sales'))

# Plot 2: Total Monthly Automobile sales using line chart.
mas = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
Y_chart2 = dcc.Graph(figure=px.line(mas,x='Month',y='Automobile_Sales',title='Total Monthly Automobile Sales'))

# Plot 3: Bar chart for average number of vehicles sold during the given year
avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata,x='Vehicle_Type',y='Automobile_Sales',
                                   title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year)
    )
)

# Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
Y_chart4 = dcc.Graph(figure=px.pie(exp_data,values='Advertising_Expenditure',names='Vehicle_Type',
                                   title='Total Advertisement Expenditure for Each Vehicle'
    )
)

return [
    html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display':'flex'}),
    html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex'})
]
