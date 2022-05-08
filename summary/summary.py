# Uruchamianie `python summary.py` (najpierw trzeba zainstalować potrzebne moduły)
# widok: http://127.0.0.1:8051/ w przeglądarce


from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# DATA

input_cnt = 30
valid_cnt = 28
dfDatabases = pd.DataFrame({
    "Database":["Pfam", "PDB", "Uniprot"],
    "Count": [10,5,13]
})



# PLOTS

db_pie = px.pie(dfDatabases, values="Count", names="Database", hole=0.1)


# SECTION COMPONENTS

# General Summary
cards = [
    dbc.Card(
        [
            html.H4("Query:", className="card-text"),
            html.P(f"tu id albo nazwa pliku", className="card-title"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    dbc.Card(
        [
            html.P("Entries:", className="card-text"),
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



# SECTIONS

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
                    html.H3("Structure Search Report"),
                    html.H4("jakiś tekst"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="download-alphafold-button", children="DOWNLOAD AlphaFold predictions", n_clicks=0
                    ),
                ],
            ),
        ],
    )

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



def build_general_summary():
    return dbc.Container(
        id="general-summary",
        children =[

            html.Hr(),
            dbc.Row([dbc.Col(card) for card in cards]),
            html.Br(),
            html.Div(
                id='db-summary',
                children = [

                    html.H4('Identificators - database'),
                    dcc.Graph(
                        id='db-summary-graph',
                        figure=db_pie
                    )
            ]),

    ])


def build_uniprot_summary_section():
    return dbc.Container(
        id="uniprot-summary")

def build_pfam_domains_summary():
    return dbc.Container(
        id="pfam-domains-summary")


def alpha_fold_predictions_section():
    return dbc.Container(
        id="alpha-fold-predictions")


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




# HTML LAYOUT
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
                build_pfam_domains_summary()


                #build_example(),
            ],
        ),
    ],
    fluid = False
)




if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

