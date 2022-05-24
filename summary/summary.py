# Uruchamianie `python app.py` (najpierw trzeba zainstalować potrzebne moduły)
# widok: http://127.0.0.1:8052/ w przeglądarce



def summary(filename, searching_summary, plddt_data):

    from dash import Dash, html, dcc
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import pandas as pd



    # ARGUMENTY:
    # searching_statistics --> [not_found_num, Pfam_ids_num, PDB_inds_num, Uniprot_ids_num, total_structures_found, alphafold_structures_num]
    # plddt_data --> ID: str | pLDDT: List(float)

    filename_or_queryname = filename
    not_found, pfam, pdb, uniprot, total, alphafold = searching_summary
    plddt_data = plddt_data




    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])




    # DATA PREPROCESSING

    from statistics import mean
    #plddt_data: ID | pLDDT | mean_plddt
    plddt_data.insert(loc=2, column="mean_plddt", value = list(map( mean, plddt_data["pLDDT"])))

    #converting plddt lists to dataframe ID | plddt_res_1  | ... | plddt res_n
    plddt_df =  pd.DataFrame(list(plddt_data["pLDDT"]))
    plddt_df.insert(0, 'IDs', plddt_data["IDs"])

    # dataframe with pldd residue-wise statistics | mean_plddt_per_residue | residues_total_cnt
    plddt_statistics = pd.DataFrame()
    plddt_statistics.insert(loc=0,column="mean_residue_plddt", value=plddt_df.iloc[:,1:].mean(axis=0))
    plddt_statistics.insert(loc=1,column="residues_count", value=plddt_df.iloc[:,1:].count(axis=0))


    # PREPARING DATA FOR PLOTS AND SUMMARIES
    query = filename_or_queryname #input id or name of input file

    entries_found = pfam +pdb + uniprot
    entries_total = entries_found + not_found  #number of id's in input file (1 if id was passed)
    structures_found = total #how many structures were found for given entries
    predictions_found = alphafold




    df_empty = pd.DataFrame({
        "x-data": [],
        "y-data": [],})





    # GENERATING PLOTS

    ## General Summary

    # databases counts pie-plot
    db_pie = px.pie(values=[pfam, pdb, uniprot], names=["Pfam", "PDB", "UniProt"], hole=0.1)


    ## AlphaFold Short Summary

    #rozkład średniego plddt dla struktur (histogram) (i długości tych struktur) (może min i max do tego)
    plddt_means_histogram = px.histogram(plddt_data,
                                        x="mean_plddt",
                                        title="Mean pLDDT values in detected predictions")
    plddt_means_histogram.update_xaxes(range=[round(min(plddt_data["mean_plddt"])-0.5,0) - 1, round(max(plddt_data["mean_plddt"])+0.5,0) + 1])
    plddt_means_histogram.update_yaxes(automargin=True)
    plddt_means_histogram.update_layout(
                                    xaxis = dict(
                                        tickmode = 'linear',
                                        tick0 = 0,
                                        dtick = 1),
                                    xaxis_title="Mean prediction's pLDDT",
                                    yaxis_title="Number of structures")



    #(wykresy pudełkowe z plddt dla najlepszych 2 i najgorszych 2 struktur względem średniego plddt)

    #średnie plddt na pozycję w białku (czerwoną pionową linią odkreślone, dokąd sięgaja wszystkie białka; może podane, ile białek jest liczonych)
    mean_plddt_per_residue = px.line(list(map(lambda x: round(x,2), plddt_statistics["mean_residue_plddt"])),
                                        markers=False,
                                        title="Mean per-residue pLDDT in detected predictions")
    mean_plddt_per_residue.add_vline(
                                x=plddt_statistics.index[plddt_statistics["residues_count"]==plddt_statistics["residues_count"][0]][-1],
                                annotation_text="Length of the shortest protein",
                                line_width=3,
                                line_dash="dash",
                                line_color="blue")
    mean_plddt_per_residue.update_layout(
                                xaxis_title="Residue number",
                                yaxis_title="Mean pLDDT",
                                showlegend=False)


    #wykres przebiegu plddt dla residuów w białku o najlepszym średnim plddt (przy świrowaniu można zrobić custom dla każdej struktury)
    plddt_maxmean = plddt_data.iloc[plddt_data["mean_plddt"].idxmax()]["pLDDT"]
    plddt_maxstructure = px.line( list(map(lambda x: round(x,2), plddt_maxmean)),
                                    title="Prediction's per-residue pLDDT"
                            )
    plddt_maxstructure.update_layout(
                                xaxis_title="Residue number",
                                yaxis_title="pLDDT",
                                showlegend=False)


    empty_plot = px.bar(df_empty, x="x-data", y="y-data", barmode="group")





    # SECTION COMPONENTS

    # section summary tabs
    general_cards = [
        dbc.Card(
            [
                html.P("Query:", className="card-text"),
                html.H4(query, className="card-title"),
            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("Input dentificators detected:", className="card-text"),
                html.H4(f"{entries_total}", className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Identificators found:", className="card-text"),
                html.H4(f" {entries_found} / {entries_total} ", className="card-title"),
                
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

    alphafold_short_cards = [
        dbc.Card(
            [
                html.P("Predictions found for:", className="card-text"),
                html.H4(f"{predictions_found}/{structures_found} structures", className="card-title"),
            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("Structure with higest mean pLDDT score:", className="card-text"),
                html.H4(("IDDD: "+ str(round(plddt_data["mean_plddt"].max(),2))), className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Structure with lowest mean pLDDT score:", className="card-text"),
                html.H4(("IDDD:  "+ str(round(plddt_data["mean_plddt"].min(),2))), className="card-title"), 
                
            ],
            body=True,
            color="light",
            inverse=False,
        ),]




    # SEKCJE 

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

    # ====== general summary ======

    def build_general_summary():
        #wyświetlanie górnego podsumowania
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
                        html.H4('Entries types'),
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
                        html.P("[Maria]"),
                        html.Br(),
                        dcc.Graph(
                            id='uniprot-graph1',
                            figure=empty_plot
                        ),
                    ],
                )],
            )


    def build_alphafold_short_summary():
        # najlepsza predykcja
        # plddt
        return dbc.Container(
            id="alpha-fold-short",
            children=[
                html.H3(f"AlphaFold short summary", className="card-title"),
                html.Hr(),
                dbc.Row([dbc.Col(card) for card in alphafold_short_cards]),

                dbc.Container(id='alphafold_mean_plddt',
                    children = [
                        html.Br(),
                        html.H4("Mean pLDDTs"),
                        dcc.Graph(
                            figure= plddt_means_histogram),
                        ],
                    ),
                dbc.Container(
                            id='alphafold_mean_plddt_per_residue',
                            children = [
                                html.Br(),
                                html.H4("Mean pLDDT per residue"),
                                dcc.Graph(
                                    figure= mean_plddt_per_residue),
                                ],
                            ), 
                dbc.Container(
                            id='best-structure-plddt-per-residue',
                            children = [
                                html.Br(),
                                html.H4("Per-residue pLDDT in prediction with maximal mean pLDDT"),
                                dcc.Graph(
                                    figure= plddt_maxstructure),
                                ],
                            ),        


               
            ],)




    def build_alphafold_summary_section():
        # przeglądanie top 50 struktur
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




    # LAYOUT
    app.layout = dbc.Container(
        id="big-app-container",
        children=[

            build_banner(),

            # Main report body
            dbc.Container(
                id="app-container",
                children=[

                    build_tabs(),

                ],
            ),
        ],
        fluid = False
    )



    app.run_server(debug=True, port=8052)




