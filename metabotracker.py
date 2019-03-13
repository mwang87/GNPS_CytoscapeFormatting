import pandas as pd
import os
#from pyMolNetEnhancer import *
import networkx as nx

def metabotracker_wrapper(input_graphml_filename, output_graphml_filename, curated_compound_names_filename="metabotracker/GNPS_Curated_Source_Information_Version2_0.tsv", source="drug"):
    curated_compound_names_df = pd.read_csv(open(curated_compound_names_filename, encoding="ascii", errors="backslashreplace"), encoding='ascii', engine='c', sep = '\t')

    input_network = nx.read_graphml(input_graphml_filename)
    output_network = metabotracker_filter(input_network, curated_compound_names_df)
    nx.write_graphml(output_network, output_graphml_filename)

def metabotracker_filter(input_graphML, curated_compound_names_df, source='drug'):
    sel = curated_compound_names_df[curated_compound_names_df['Source']== source]['GNPS_annotation'].tolist()

    # select all nodes with library matches within selecte source category
    sel_ids = list()

    for v in input_graphML.nodes():
        if 'Compound_Name' in input_graphML.node[v]:
            if input_graphML.node[v]['Compound_Name'] in sel:
                sel_ids.append(v)

    # select all neighbours of the library matches
    sel_ids_neigh = list()

    for t in sel_ids:
        sel_ids_neigh.append([n for n in input_graphML.neighbors(str(t))])

    sel_ids_neigh = list(set([item for sublist in sel_ids_neigh for item in sublist]))

    # combine nodes with library matches and neighbours and create subgraph
    sel_ids_final = list(set(sel_ids_neigh + sel_ids))

    H = input_graphML.subgraph(sel_ids_final)

    return H
