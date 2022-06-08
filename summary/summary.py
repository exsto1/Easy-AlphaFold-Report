def generate_summary(filename, extra_info, plddt_data, type_df, uni_data):

    from dash import Dash, html, dcc
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import pandas as pd
    from statistics import mean


    # ARGUMENTY:
    # filename --> nazwa wejściowego pliku lub wejściowy kod
    # extra_info = [count_found, len(FAMILIES), len(PDB), len(UNIPROT), len(Uni_IDs), len(ALPHA_IDS)]
    # plddt_data --> "IDs": str | "pLDDT": List(float)
    # uni_data


    #print("filename:", filename)
    #print("extra_info: ", extra_info)
    #print("plddt_data", plddt_data)
    #print("type_df", type_df)






    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



    ########################################################
    # DATA PREPROCESSING



    ### Gosia -- preprocessing ###

    # database entries counts
    pfam = (type_df.Database.values == "Pfam").sum()
    pdb = (type_df.Database.values == "PDB").sum()
    uniprot = (type_df.Database.values == "Uni").sum()
    not_found = (type_df.Database.values == "None").sum()
    entries_found = pfam +pdb + uniprot

    total_uniprot, alphafold = extra_info[-2:]

    # mean plddt's for structures -- as an additional column in plddt_data
    #plddt_data: ID | pLDDT | mean_plddt
    plddt_data.insert(loc=2, column="mean_plddt", value = list(map( mean, plddt_data["pLDDT"])))

    #dataframe with plddt lists converted to columns to ID | plddt_res_1  | ... | plddt res_n
    plddt_df =  pd.DataFrame(list(plddt_data["pLDDT"]))
    plddt_df.insert(0, 'IDs', plddt_data["IDs"])

    # dataframe with pldd residue-wise statistics | mean_plddt_per_residue | residues_total_uniprot_cnt
    plddt_statistics = pd.DataFrame()
    plddt_statistics.insert(loc=0,column="mean_residue_plddt", value=plddt_df.iloc[:,1:].mean(axis=0))
    plddt_statistics.insert(loc=1,column="residues_count", value=plddt_df.iloc[:,1:].count(axis=0))

    ### Gosia preprocessing end ###








    #############################################
    # GENERATING PLOTS

    ## Gosia -- plots start ##

    ## General summary
    #db_pie = px.pie(values=[pfam, pdb, uniprot, not_found], names=["Pfam", "PDB", "UniProt", "NotFound"], hole=0.1)
    db_pie = px.pie(values=[pfam, pdb, uniprot, not_found],
                    names=["Pfam", "PDB", "UniProt", "Not Found"],
                    title="Recognized input ID\'s:",
                    hole=0.1)


    ## AlphaFold Short Summary Section
    #mean plddt histogram
    plddt_means_histogram = px.histogram(plddt_data,
                                        x="mean_plddt",
                                        title="Mean pLDDT values in AlphaFold predictions")
    plddt_means_histogram.update_xaxes(range=[round(min(plddt_data["mean_plddt"])-0.5,0) - 1, round(max(plddt_data["mean_plddt"])+0.5,0) + 1])
    plddt_means_histogram.update_yaxes(automargin=True)
    plddt_means_histogram.update_layout(
                                    xaxis = dict(
                                        tickmode = 'linear',
                                        tick0 = 0,
                                        dtick = 1),
                                    xaxis_title="Mean prediction's pLDDT",
                                    yaxis_title="Number of structures")


    # mean plddt per-position 
    mean_plddt_per_residue = px.line(list(map(lambda x: round(x,2), plddt_statistics["mean_residue_plddt"])),
                                        markers=False,
                                        title="Mean per-residue pLDDT in AlphaFold predictions")
    mean_plddt_per_residue.add_vline(
                                x=plddt_statistics.index[plddt_statistics["residues_count"]==plddt_statistics["residues_count"][0]][-1],
                                annotation_text="Length of the shortest protein",
                                line_width=3,
                                line_dash="dash",
                                line_color="blue")
    mean_plddt_per_residue.update_layout(
                                xaxis_title="Residue index",
                                yaxis_title="Mean pLDDT",
                                showlegend=False)


    # plddt-per residue for prediction with best plddt
    plddt_maxmean = plddt_data.iloc[plddt_data["mean_plddt"].idxmax()]["pLDDT"]
    plddt_maxstructure = px.line( list(map(lambda x: round(x,2), plddt_maxmean)),
                                    title="Prediction's per-residue pLDDT"
                            )
    plddt_maxstructure.update_layout(
                                xaxis_title="Residue index",
                                yaxis_title="pLDDT",
                                showlegend=False)

    ### Gosia plots end ###



    #########################################################
    # SECTION COMPONENTS
    # sections' summary tabs
    # Gosia
    general_cards = [
        dbc.Card(
            [
                html.P("Results for:", className="card-text"),
                html.H4(filename, className="card-title"),
            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("Input ID's:", className="card-text"),
                html.H4(f"{entries_found + not_found}", className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Recognized input ID's:", className="card-text"),
                html.H4(f" {entries_found} / {entries_found + not_found} ", className="card-title"),
                
            ],
            body=True,
            color="primary",
            inverse=True,
        ),]
    # Gosia -- Maria -- uzupełnić zawartość kafelek
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
    # Gosia
    alphafold_short_cards = [
        dbc.Card(
            [
                html.P("AlphaFold predictions found for:", className="card-text"),
                html.H4(f"{total_uniprot} / {alphafold}  final UniProt structures", className="card-title"),

            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("UniProt ID for structure with higest mean pLDDT:", className="card-text"),
                html.H4((f"{plddt_data.iloc[plddt_data['mean_plddt'].idxmax(),0]}:  "+ str(round(plddt_data["mean_plddt"].max(),2))), className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Predictions' mean pLDDT score:", className="card-text"),
                html.H4( (f" {round(mean(plddt_data['mean_plddt']),2)}" ) , className="card-title"), 
                
            ],
            body=True,
            color="light",
            inverse=False,
        ),]



    #########################################################
    # SECTIONS 

    # Gosia
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

            ],
        )
    # Gosia
    def build_tabs():
        return html.Div(
            id="tabs",
            className="tabs",
            children=[


                dcc.Tabs(
                    id="app-tabs",
                    value="tab1",
                    className="custom-tabs",
                    children=[
                        dcc.Tab(
                            id="general-summary-tab",
                            label="General Summary",
                            value="tab1",
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                            children=[
                                build_general_summary(),
                                build_uniprot_summary_section(),
                                build_alphafold_short_summary(),

                            ],
                        ),
                        dcc.Tab(
                            id="alphafold_predictions",
                            label="AlphaFold Predictions",
                            value="tab2",
                            className="custom-tab",
                            children =[
                                build_alphafold_summary_section(),

                            ],
                        ),
                    ],
                )
            ],




        )
    # Gosia
    def build_general_summary():

        return dbc.Container(
            id="general-summary",
            children =[

                html.H3(f"Input Statistics", className="card-title"),
                html.Hr(),
                dbc.Row([dbc.Col(card) for card in general_cards]),
                html.Br(),


                dbc.Container(
                    id='db-summary',
                    children = [
                        dcc.Graph(
                            id='db-summary-graph',
                            figure=db_pie
                        ),
                        html.P(f"Results of searching for provided ID's in Pfam, PDB and UniProt databases (results: Pfam: {pfam}, PDB: {pdb}, Uniprot: {uniprot})."),
                        html.P(f"Not recognized identifiers: {not_found}."),

                ]),
        ])
    # Maria -- uzup.
    def build_uniprot_summary_section():
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
                        html.P("[Maria]"),
                        html.Br(),
                        dcc.Graph(
                            id='uniprot-graph1',
                        ),
                    ],
                )],
            )

    # Gosia
    def build_alphafold_short_summary():
        return dbc.Container(
            id="alpha-fold-short",
            children=[
                html.H3(f"AlphaFold short summary", className="card-title"),
                html.Hr(),
                dbc.Row([dbc.Col(card) for card in alphafold_short_cards]),

                dbc.Container(id='alphafold_mean_plddt',
                    children = [
                        html.Br(),
                        html.H4("General pLDDT info"),
                        dcc.Graph(
                            figure= plddt_means_histogram),
                        ],
                    ),
                dbc.Container(
                            id='alphafold_mean_plddt_per_residue',
                            children = [
                                html.Br(),
                                html.H4("Per-residue pLDDT"),
                                dcc.Graph(
                                    figure= mean_plddt_per_residue),
                                ],
                            ), 
                dbc.Container(
                            id='best-structure-plddt-per-residue',
                            children = [
                                html.Br(),
                                html.H4(f"Structure with maximal mean pLDDT ({plddt_data.iloc[plddt_data['mean_plddt'].idxmax(),0]}:  { round( plddt_data['mean_plddt'].max() , 2 ) })"),
                                dcc.Graph(
                                    figure= plddt_maxstructure),
                                ],
                            ),        
     
            ],)

    # Maria -- uzup.
    def build_alphafold_summary_section():
        return dbc.Container(
            id="alpha-fold-predictions",
            children=[
                html.H3(f"AlphaFold predictions gallery", className="card-title"),
                html.Hr(),
                html.Br(),
                html.H4('[przegląd top predykcji z alphafold]'),
                html.Br(),
                dbc.Container(
                    
                    children = [
                        html.Br(),
                        dcc.Graph(
                        ),
                    ],
                )
            ]

            )


    ########################################################
    # LAYOUT
    app.layout = dbc.Container(
        id="big-app-container",
        children=[

            build_banner(),
            dbc.Container(
                id="app-container",
                children=[

                    build_tabs(),

                ],
            ),
        ],
        fluid = False
    )



    app.run_server(debug=False, port=8052)
