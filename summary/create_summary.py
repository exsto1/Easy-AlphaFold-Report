# Uruchamianie `python app.py` (najpierw trzeba zainstalować potrzebne moduły)
# widok: http://127.0.0.1:8051/ w przeglądarce


from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



# DANE

## GeneralSection data
input_cnt = 30
valid_cnt = 28

dfDatabases = pd.DataFrame({
    "Database":["Pfam", "PDB", "Uniprot"],
    "Count": [10,5,13]
})


## Pfam Section data
df_domains = pd.DataFrame({
    "Domain": ["A", "B", "C", "D", "E"],
    "Occurences": [10, 17, 20, 1, 9],
})

df_empty = pd.DataFrame({
    "x-data": [],
    "y-data": [],
})


## AlphaFold Short data
# przykład z palca a'la plddt
import random
import numpy

random_float_array = numpy.random.uniform(30, 100, 1000)
random_float_array = list(map(lambda x: round(x,2), random_float_array))




# WYKRESY

## General
db_pie = px.pie(dfDatabases, values="Count", names="Database", hole=0.1)

## Pfam domains
pfam_domains = px.bar(df_domains, x="Domain", y="Occurences", barmode="group")

## AlphaFold short
#heatmap = px.imshow(..data.., color_continuous_scale='RdBu_r', origin='lower')
empty_plot = px.bar(df_empty, x="x-data", y="y-data", barmode="group")




# ELEMENTY SKŁADOWE DO SEKCJI

# GeneralSummary
general_cards = [
    dbc.Card(
        [
            html.P("Query:", className="card-text"),
            html.H4(f"tu id albo nazwa pliku", className="card-title"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),

    dbc.Card(
        [
            html.P("Entries total:", className="card-text"),
            html.H4(f"{input_cnt}", className="card-title"),   
        ],
        body=True,
        color="light",
        inverse=False,
    ),


    dbc.Card(
        [
            html.P("Entries found:", className="card-text"),
            html.H4(f" {valid_cnt} / {input_cnt} ", className="card-title"),
            
        ],
        body=True,
        color="primary",
        inverse=True,
    ),]

uniprot_cards = [
    dbc.Card(
        [
            html.P("Info 1", className="card-text"),
            html.H4(f"info", className="card-title"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),

    dbc.Card(
        [
            html.P("Info 2:", className="card-text"),
            html.H4(f"info", className="card-title"),   
        ],
        body=True,
        color="light",
        inverse=False,
    ),


    dbc.Card(
        [
            html.P("Info 3:", className="card-text"),
            html.H4(f"info", className="card-title"),
            
        ],
        body=True,
        color="light",
        inverse=False,
    ),]

pfam_cards = [
    dbc.Card(
        [
            html.P("Total number of domains found:", className="card-text"),
            html.H4(f"{10}", className="card-title"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),

    dbc.Card(
        [
            html.P("Higest occurence rate:", className="card-text"),
            html.H4(f"{10}", className="card-title"),   
        ],
        body=True,
        color="light",
        inverse=False,
    ),


    dbc.Card(
        [
            html.P("Domains occurence statistics:", className="card-text"),
            html.H4(f" ...tu proste podsumowania...  ", className="card-title"),
            
        ],
        body=True,
        color="light",
        inverse=False,
    ),]

alphafold_short_cards = [
    dbc.Card(
        [
            html.P("Predictions found for:", className="card-text"),
            html.H4(f"{6}/{10} structures", className="card-title"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),

    dbc.Card(
        [
            html.P("Best mean pLDDT score:", className="card-text"),
            html.H4(f"{90}", className="card-title"),   
        ],
        body=True,
        color="light",
        inverse=False,
    ),


    dbc.Card(
        [
            html.P("Worsst mean pLDDT score:", className="card-text"),
            html.H4(f"{10}", className="card-title"), 
            
        ],
        body=True,
        color="light",
        inverse=False,
    ),]




# SEKCJE 

# Banner
#todo:
    #zmienić na bootstrap
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H2("Structure Search Report"),
                ],
            ),
            html.Br(),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="download-alphafold-button", children="DOWNLOAD AlphaFold predictions", n_clicks=0
                    ),
                    html.P("guzik do potencjalnego pobrania plików ze strukturami; będzie ładniejszy i z prawej")
                ],
            ),
        ],
    )

# Tabs
#todo:
    #zmienić na bootstrap
def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="summary-tab",
                        label="Summary",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="alphafold_predictions",
                        label="AlphaFold Predictions",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )




# SECTIONS

def build_general_summary():
    #wyświetlanie górnego podsumowania
    return dbc.Container(
        id="general-summary",
        children =[

            html.H3(f"Input Summary", className="card-title"),
            html.Hr(),
            dbc.Row([dbc.Col(card) for card in general_cards]),
            html.Br(),
            dbc.Container(
                id='db-summary',
                children = [
                    html.H4('Entries type'),
                    html.P('To będzie mniej rozstrzelone'),
                    dcc.Graph(
                        id='db-summary-graph',
                        figure=db_pie
                    )
            ]),

    ])


def build_uniprot_summary_section():
    #   2.1. dla ilu/których znaleziono struktury krystalograficzne
    #   2.2. rozdzielczość najlepszej struktury z krystalografii (i dla której ze struktur) / ew zestawienie jakości struktur eksperymentalnych
    #   2.3 (długość/masa?)
    #   2.4 ile (pojedynczo/średnio) mają różnych partnerów białkowych
    return dbc.Container(
        id="uniprot-summary",
        children=[
            html.H3(f"Uniprot Summary", className="card-title"),
            html.Hr(),
            dbc.Row([dbc.Col(card) for card in uniprot_cards]),
            html.Br(),
            html.Br(),
            dbc.Container(
                id='uniprot-c1',
                children = [
                    html.Br(),
                    html.P("Sekcja z podsumowaniami danych o białkach z Uniprot. (robi Maria)"),
                    html.H4('Tu bedą wykresy (w tej sekcji najwięcej)'),
                    html.Br(),
                    dcc.Graph(
                        id='uniprot-graph1',
                        figure=empty_plot
                    ),
                ],
            )],
        )

def build_pfam_domains_summary():
    # ile domen współwystępujących 
    # jaka częstość których (wykres obcięty do np. najczęstszych, jesli dużo)
    return dbc.Container(
        # total number of domains found  # higest occurence rate (rate and name) # Domains occurence statistics (min domains no max, mean, median)
        id="pfam-domains-summary",
        children =[

            html.H3(f"Other Domains Found", className="card-title"),
            html.Hr(),
            dbc.Row([dbc.Col(card) for card in pfam_cards]),
            html.Br(),
            html.Br(),
            dbc.Container(
                id='pfam-domains-barplot',
                children = [
                    html.Br(),
                    html.H4('Sekcja z podsumowaniami dotyczącymi występowania domen poza szukaną'),
                    html.P("Podsumowania liczbowe i wykresy"),
                    html.H4('Other domains frequency'),
                    dcc.Graph(
                        id='pfam-domains-graph',
                        figure=pfam_domains
                    )
            ]),

    ])





def build_alphafold_short_summary():
    # najlepsza predykcja
    # plddt
    return dbc.Container(
        id="alpha-fold-short",
        children=[
            html.H3(f"AlphaFold [short summary]", className="card-title"),
            html.Hr(),
            dbc.Row([dbc.Col(card) for card in alphafold_short_cards]),
            dbc.Container(
                id='alph-c1',
                children = [
                    html.Br(),
                    html.H4("Tu dane z alphafold."),
                    html.P("co chcemy tu pokazać? jaka wizualizacja plddt?"),
                    dcc.Graph(
                        figure=empty_plot
                    ),
                ],
            )

           
        ]

)



def build_alphafold_summary_section():
    # przeglądanie top 50 struktur
    return dbc.Container(
        id="alpha-fold-predictions",
        children=[
            html.H3(f"AlphaFold predictions gallery", className="card-title"),
            html.Hr(),
            html.Br(),
            html.H4('To będzie w osobnej zakładce - sekcja z przeglądem top min{znalezione, n=const} struktur z alphafold'),
            html.P("Struktury (i odnośniki?)"),
            html.P("na górze opcja pobrania plików z ciffami / pdbami (zostaje?)"),
            html.Br(),
            dbc.Container(
                
                children = [
                    html.Br(),
                    dcc.Graph(
                        figure=empty_plot
                    ),
                ],
            )
        ]

        )







def build_example():
    return html.Div(children=[

                html.H1(children='General Summary'),

                    #załącz wykres
                    dcc.Graph(
                        id='example-graph',
                        figure=fig
                    ),

                    #załącz wykres
                    dcc.Graph(
                        id='databases_pieplot',
                        figure=db_pie
                    )
                ]
            )




# WYGLĄD htmla
app.layout = dbc.Container(
    id="big-app-container",
    children=[

        build_banner(),

        # Main report body
        dbc.Container(
            id="app-container",
            children=[

                build_tabs(),
                build_general_summary(),
                build_uniprot_summary_section(),
                build_pfam_domains_summary(),
                build_alphafold_short_summary(),
                build_alphafold_summary_section(),


                #build_example(),
            ],
        ),
    ],
    fluid = False
)




if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
