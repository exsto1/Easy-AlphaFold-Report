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


    ####### ------------------------------------------------------------------------------------------------
    # LICZENIE DŁUGOŚCI
    #filename -- lista[[ID],[scieżki]] # zawsze dwie 
    sections_lengths = [len(i) for i in filename]
    total_section_length = sum(sections_lengths)

    ######  ^^^ total section length 1 gdy będzie dokładnie jeden plik/ID z okienka/terminala
    ####### ------------------------------------------------------------------------------------------------



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
                    title="Percent of input ID\'s found in Pfam / UniProt / PDB databases:",
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

    if total_section_length == 1:
        query = filename[0][0] if len(filename[0])!=0 else filename[1][0] # query is either a single ID or single filepath 
        query = query.split('/')[-1]

        query_card = dbc.Card(
                        [
                            html.P("Results for input ID / file:\n", className="card-text"),
                            html.P(""),
                            html.H4(query, className="card-title"),
                        ],
                        body=True,
                        color="dark",
                        inverse=True,
                    )
    else:
        query_card = dbc.Card(
                        [
                            html.P("Number of input IDs/files:\n", className="card-text"),
                            html.P(""),
                            html.H4(total_section_length, className="card-title"),
                            
                            
                        ],
                        body=True,
                        color="dark",
                        inverse=True,
                    )






    general_cards = [
        query_card,

        dbc.Card(
            [
                html.P("Total number of input ID's (provided directly or in files):", className="card-text"),
                html.H4(f"{entries_found + not_found}", className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Identifiers recognized as Pfam / UniProt / PDB entries:", className="card-text"),
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
                html.P("Total number of UniProt entries connected with given input:", className="card-text"),
                html.H4(f"{total_uniprot}", className="card-title"),
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
                html.H4(f"{alphafold} / {total_uniprot}    UniProt structures", className="card-title"),

            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("UniProt ID for structure with highest mean pLDDT:", className="card-text"),
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

                        dcc.Tab(
                            id="alphafold_hyperlinks",
                            label="AlphaFold Links",
                            value="tab3",
                            className="custom-tab",
                            children =[
                                build_alphafold_links(),
                            ],
                        ),
                    ],
                )
            ],




        )
    # Gosia
    def build_general_summary():

        if not_found == 0:
            not_recognized_info = ""
        elif not_found ==1:
            not_recognized_info = f"There had been: {not_found} input identifier passed directly as ID or in input files, not found in Pfam / UniProt / PDB databases."
        else:
            not_recognized_info = f"There had been: {not_found} input identifiers passed directly as ID or in input files, which were not found in Pfam / UniProt / PDB databases."

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
                        html.P(not_recognized_info),

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



    ###############################
    # do kontenera w tej funkcji wstawiamy rzeczy, które mają pojawiać się w trzeciej zakładce
    # (można też dopisać więcej funkcji zwracających rzeczy do tej zakładki -- każdą wtedy trzeba podlinkować w zakładce 3 (id="alphafold_hyperlinks"))
    ##############################
    def build_alphafold_links():
        return dbc.Container(
            id="alpha-fold-links",
            children=[
                html.H3(f"Tutaj linki", className="card-title"),
                html.Hr(),
                html.Br(),
                html.H4('[click click]'),
                html.A('AlphaFold', href = 'https://alphafold.ebi.ac.uk'),
                html.Br(),
                dbc.Container(

                ),
            ],

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
