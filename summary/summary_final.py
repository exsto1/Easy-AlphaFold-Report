def generate_summary(filename, extra_info, plddt_data, type_df, uni_data):

    from dash import Dash, html, dcc, dash_table
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    from statistics import mean

    import dash_bio as dashbio
    from dash_bio.utils import PdbParser, create_mol3d_style
    from dash.dependencies import Input, Output


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

    ### Maria preprocessing ####

    structures = plddt_data.sort_values(by=['mean_plddt'], ascending=False)[['IDs', 'mean_plddt']]
    if structures.shape[0] < 50:
        structures_50 = pd.concat([structures[:1], structures[-1:], structures[1:-1]])
    else:
        structures_50 = pd.concat([structures[:1], structures[-1:], structures[1:50]])
    
    parser = [PdbParser(f"config/data/temp/{name}.cif") for name in structures_50['IDs']]
    data = [p.mol3d_data() for p in parser]
    styles = [create_mol3d_style(
        d['atoms'], visualization_type='cartoon', color_element='residue'
    ) for d in data] 

    uniprot_data = uni_data
    
    #Uniprot - length
    uniprot_data['Length'] = [int(x) for x in uniprot_data['Length']]
    #number structures found
    num_of_str = uniprot_data.shape[0]
    #percent of reviewed structures 
    rev_perc = (uniprot_data[uniprot_data['Reviewed']=='reviewed'].shape[0]/uniprot_data.shape[0])*100
    #average protein length 
    avg_len = uniprot_data["Length"].mean()
    
    #Lineage
    lineage_data = uniprot_data[['Superkingdom', 'Genus']]
    lineage_data = lineage_data.fillna('Unclassified')
    lineage_data.loc[lineage_data['Genus'] == "", "Genus"] = "Unclassified"
    lineage_data.loc[lineage_data['Superkingdom'] == "", "Superkingdom"] = "Unclassified"

    lin_parents = []
    lin_labels = []
    lin_counts = []

    groups_1 = lineage_data.groupby(['Superkingdom']).groups
    for group in groups_1:
        lin_parents.append("")
        lin_labels.append(group)
        lin_counts.append(len(groups_1[group]))
    groups_2 = lineage_data.groupby(['Superkingdom', 'Genus']).groups
    for group in groups_2: 
        if group[0] != 'Unclassified':
            lin_parents.append(group[0])
            lin_labels.append(group[1])
            lin_counts.append(len(groups_2[group]))
    
    #PDB - ids
    #how many have pdb structure 
    have_pdb = uniprot_data[uniprot_data['PDB'].notnull()]

    #table with pdb structures
    pdb_ids = uniprot_data[uniprot_data['PDB']!= ""][['Entry', 'PDB']]
    pdb_ids['PDB'] = pdb_ids['PDB'].apply(lambda x: x[:-1].split(";"))
    pdb_ids = pdb_ids.explode('PDB')
    pdb_ids = pdb_ids.reset_index(drop=True)
    pdb_ids.rename({'Entry': 'Uniprot'}, axis=1, inplace=True)
    
    #Pfam
    #Number of Pfam domains per structure
    n_of_domains = uniprot_data[['Entry', 'Pfam']]
    n_of_domains = n_of_domains.fillna(0)
    n_of_domains['Pfam'] = n_of_domains['Pfam'].map(lambda x: len(x) if x!=0 else 0)

    #Most frequent Pfam domains
    pfam_ids = uniprot_data[uniprot_data['Pfam'].notnull()][['Entry', 'Pfam']]
    pfam_ids = pfam_ids.explode('Pfam')
    pfam_ids = pfam_ids['Pfam'].value_counts().rename_axis('Pfam domain').reset_index(name='Counts')
    pfam_ids = pfam_ids[pfam_ids['Counts']>=1]

    ### Maria preprocessing end ####


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

    ### Generating plots - Maria ###

    def pdb_table():
        if pdb_ids.shape[0] != 0:
            return dash_table.DataTable(
                        data=pdb_ids.to_dict('records'),
                        columns=[{'id': c, 'name': c} for c in pdb_ids.columns],
                        page_action='none',
                        style_cell={'textAlign': 'left'},
                        style_table={'height': '300px', 'overflowY': 'auto'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white'
                        }
                    )
        else: 
            return  html.H5("No entries with known 3D structures")

    #Protein lengths plots

    len_plot = go.Figure()
    len_plot.add_trace(go.Histogram(y=uniprot_data['Length']))

    len_plot.update_xaxes(automargin=True)
    len_plot.update_yaxes(automargin=True)
    len_plot.update_layout(title='Protein length distibution',yaxis_title="Number of amino acids", xaxis_title="Count")
    
    #Number of Pfam domains per structure
    n_of_domains_hist = go.Figure()
    n_of_domains_hist.add_trace(go.Histogram(x=n_of_domains["Pfam"]))
    n_of_domains_hist.update_layout(yaxis_title="Number of records", xaxis_title="Number of Pfam domains")
    
    #Most frequent Pfam domains
    pfam_domains = go.Figure()
    pfam_domains.add_trace(go.Histogram(histfunc="sum", y=pfam_ids['Counts'], x=pfam_ids['Pfam domain'], name="sum"))
    pfam_domains.update_layout(yaxis_title="Number of records", xaxis_title="Pfam Domain")
    
    #Lineage - sunburst 
    lineage_plot = go.Figure(go.Sunburst(
    labels=lin_labels,
    parents=lin_parents,
    values=lin_counts,
    branchvalues="total",
    ))
    lineage_plot.update_layout(
    margin = dict(t=10, l=10, r=10, b=10)
    )

    ### Alphafold structures visualization
    def mol_visualize(ind:int):

        if ind==0:

            cards = dbc.Container(

                id="best-structure",
                children = [

                    dbc.Row([
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.P("Molecule with the highest pLDDT value:", className="card-text"),
                                    html.H4(f"{structures_50['IDs'][ind]}", className="card-title"),
                                ],
                                body=True,
                                color="success",
                                inverse=True,
                                ),
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.P("Mean pLDDT value:", className="card-text"),
                                    html.H4(f"{round(structures_50['mean_plddt'][ind], 2)}", className="card-title"),   
                                ],
                                body=True,
                                color="light",
                                inverse=False,
                                ),
                        ),
                    ]),
                ]
            )
        
        elif ind==1:

            cards = dbc.Container(

                id="worst-structure",
                children = [

                    dbc.Row([
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.P("Molecule with the lowest pLDDT value:", className="card-text"),
                                    html.H4(f"{structures_50['IDs'][ind]}", className="card-title"),
                                ],
                                body=True,
                                color="danger",
                                inverse=True,
                                ),
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.P("Mean pLDDT value:", className="card-text"),
                                    html.H4(f"{round(structures_50['mean_plddt'][ind], 2)}", className="card-title"),   
                                ],
                                body=True,
                                color="light",
                                inverse=False,
                                ),
                        ),
                    ]),
                ]
            )
        
        else:

            cards = dbc.Container(
                dbc.Row([

                    dbc.Col(
                        dbc.Card(
                            [
                                html.P("Molecule ID", className="card-text"),
                                html.H4(f"{structures_50['IDs'][ind]}", className="card-title"),
                            ],
                            body=True,
                            color="dark",
                            inverse=True,
                            ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.P("Mean pLDDT value:", className="card-text"),
                                html.H4(f"{round(structures_50['mean_plddt'][ind], 2)}", className="card-title"),   
                            ],
                            body=True,
                            color="light",
                            inverse=False,
                            ),

                    ),
                ]),
            )


        result = dbc.Container(

            id=f"mol-{ind}",
            children = [

            cards, 

            dashbio.Molecule3dViewer(
                id=f"dashbio-default-molecule3d_{ind}",
                modelData=data[ind],
                styles=styles[ind]
            ),

            "Selection data",
            html.Hr(),
            html.Div(id=f"default-molecule3d-output_{ind}")
            ],
        )

        return result

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
#Maria - uniprot
    uniprot_cards = [
        dbc.Card(
            [
                html.P("Number of structures found", className="card-text"),
                html.H4(f"{num_of_str}", className="card-title"),
            ],
            body=True,
            color="dark",
            inverse=True,
        ),

        dbc.Card(
            [
                html.P("Percentage of reviewed structures", className="card-text"),
                html.H4(f"{round(rev_perc, 2)}%", className="card-title"),   
            ],
            body=True,
            color="light",
            inverse=False,
        ),


        dbc.Card(
            [
                html.P("Average protein length:", className="card-text"),
                html.H4(f"{round(avg_len)}", className="card-title"),

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
    # Maria 
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
                id='uniprot-pdb-ids',
                children = [
                    html.Br(),
                    html.H4("Entries with known 3D structures"),
                    pdb_table()
                ],
                ),
            
                dbc.Container(
                    id='uniprot-length',
                    children = [
                        html.Br(),
                        html.H4("Protein lengths"),
                        dcc.Graph(
                            id='uniprot-len',
                            figure=len_plot
                            ),
                        ],
                ),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Container(
                            id='uniprot-pfam-count',
                            children = [
                                html.Br(),
                                html.H4("Number of Pfam domains"),
                                dcc.Graph(
                                    id='n_of_domains_hist',
                                    figure=n_of_domains_hist
                                    ),
                                ],
                            ),
                        ),
                    dbc.Col(
                        dbc.Container(
                            id='uniprot-top10-pfam',
                            children = [
                                html.Br(),
                                html.H4("Most frequent Pfam domains"),
                                dcc.Graph(
                                    id='pfam-domains',
                                    figure=pfam_domains
                                    ),
                                ],
                            ),
                        )
                ]),
                
                dbc.Container(
                    id='uniprot-lineage',
                    children = [
                        html.Br(),
                        html.H4("Lineage of the protein structures"),
                        html.Br(),
                        dcc.Graph(
                            id='uniprot-lin',
                            figure=lineage_plot
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

    # Maria 
    def build_alphafold_summary_section():
        return dbc.Container(
            id="alpha-fold-predictions",
            children=[
                html.H3(f"AlphaFold predictions gallery", className="card-title"),
                html.Hr(),
                html.Br(),
                html.H4('Top Alphafold predictions'),
                html.Br(),
                dbc.Container(
                    id='mol-visualize',
                    children = [mol_visualize(i) for i in range(structures_50.shape[0])],
                )
            ]

            )



    ###############################
    # do kontenera w tej funkcji wstawiamy rzeczy, które mają pojawiać się w trzeciej zakładce
    # (można też dopisać więcej funkcji zwracających rzeczy do tej zakładki -- każdą wtedy trzeba podlinkować w zakładce 3 (id="alphafold_hyperlinks"))
    ##############################
    def build_alphafold_links():

        # PD DATAFRAME
        # IDs | mean_plddt | link

        new_data = plddt_data[["IDs", "mean_plddt"]]
        new_data = new_data.sort_values(by="mean_plddt", ascending=False)
        new_data = new_data.reset_index(drop=True)
        new_data["link"] = new_data.apply(lambda row: f"https://alphafold.ebi.ac.uk/entry/{row['IDs']}", axis=1)

        table = dash_table.DataTable(new_data.to_dict('records'), [{"name": i, "id": i} for i in new_data.columns])


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
                    table
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

    for i in range(structures_50.shape[0]):

        @app.callback(
            Output(f'default-molecule3d-output_{i}', 'children'),
            Input(f'dashbio-default-molecule3d_{i}', 'selectedAtomIds')
        )

        def show_selected_atoms(atom_ids):
            if atom_ids is None or len(atom_ids) == 0:
                return 'No atom has been selected. Click somewhere on the molecular \
                structure to select an atom.'
            return [html.Div([
                html.Div('Element: {}'.format(data[i]['atoms'][atm]['elem'])),
                html.Div('Chain: {}'.format(data[i]['atoms'][atm]['chain'])),
                html.Div('Residue name: {}'.format(data[i]['atoms'][atm]['residue_name'])),
                html.Br()
                ]) for atm in atom_ids]



    app.run_server(debug=False, port=8052)