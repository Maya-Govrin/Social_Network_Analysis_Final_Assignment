# Leiden Algorithm: Example Implementation, Candidate Applications Bipartite Graph
# imports
import pandas as pd
from sknetwork.clustering import Leiden
from sknetwork.data import from_edge_list
import networkx as nx
import matplotlib.pyplot as plt

# Creating the candidates dataframe: Candidate university information and edges of applications to firms
candidate_metadata = pd.DataFrame({
    'candidate_id': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6',
                     'c7', 'c8', 'c9', 'c10', 'c11', 'c12'],
    'university': [
        'TAU', 'TAU', 'HUJI', 'TAU',
        'HUJI', 'HUJI', 'RUNI', 'HUJI',
        'RUNI', 'RUNI', 'RUNI', 'TAU'
    ]
})
edges = [
    ['c1', 'Meitar',10], ['c1', 'Herzog',7],
    ['c2', 'Meitar',9], ['c3', 'Herzog',8],
    ['c4', 'Meitar',8], ['c4', 'Herzog',10],['c4', 'Agmon',2],
    ['c5', 'Agmon',10], ['c5', 'Arnon',7],
    ['c6', 'Agmon',10], ['c7', 'Arnon',9],
    ['c8', 'Agmon',10], ['c8', 'Arnon',9],['c8', 'Goldfarb',3],
    ['c9', 'Goldfarb',9], ['c9', 'Fischer',10],
    ['c10', 'Goldfarb',8], ['c11', 'Fischer',9],['c11', 'Arnon',1],
    ['c12', 'Goldfarb',7], ['c12', 'Fischer',10],['c12', 'Meitar',1]

]
df_edges = pd.DataFrame(edges, columns=['candidate_id', 'firm_id','weight'])

# building the bipartite graph with weighted edges
graph = from_edge_list(
    df_edges[['candidate_id', 'firm_id', 'weight']].values.tolist(),
    bipartite=True,
    weighted=True,
    reindex=True,
    matrix_only=False
)
# creating adjacency matrix (in a bipartite network, this is table of edge and weight)
biadjacency = graph.biadjacency
names_row = list(graph.names_row)
names_col = list(graph.names_col)

# Running Leiden on the adjacency matrix of the bipartite network
leiden = Leiden()
leiden.fit(biadjacency)

# results df for candidates
candidate_results = pd.DataFrame({
    'candidate_id': names_row,
    'community': leiden.labels_row_
})
print("candidate community assignments")
print(candidate_results.sort_values('community'))

# merging with candidates university data
comparison_df = candidate_results.merge(candidate_metadata, on='candidate_id')

# university distribution across communities
analysis = pd.crosstab(comparison_df['university'], comparison_df['community'])

print("community vs. university")
print(analysis)

# firm community results
firm_results = pd.DataFrame({
    'firm_id': names_col,
    'community': leiden.labels_col_
})
print("firms community assignments")
print(firm_results.sort_values('community'))

# initialize the bipartite graph of the network
bipartite = nx.Graph()
bipartite.add_nodes_from(names_row, bipartite=0) # candidates
bipartite.add_nodes_from(names_col, bipartite=1) # firms

# weighted edges
for _, row in df_edges.iterrows():
    bipartite.add_edge(row['candidate_id'], row['firm_id'], weight=row['weight'])

# Mapping communities to colors: candidates and firms
cmap = plt.get_cmap('Dark2')
node_colors = []
for node in names_row:
    community_id = candidate_results.set_index('candidate_id').loc[node, 'community']
    node_colors.append(cmap(community_id))
for node in names_col:
    community_id = firm_results.set_index('firm_id').loc[node, 'community']
    node_colors.append(cmap(community_id))

# creating bipartite layout
pos = nx.bipartite_layout(bipartite, names_row,align="vertical", scale=1)

#drawing graph, edges thickness based on weight
plt.figure(figsize=(10, 8))

edge_widths = [bipartite[u][v]['weight'] * 0.5 for u, v in bipartite.edges()]
nx.draw(bipartite, pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        font_size=10,
        width=edge_widths,
        edge_color='gray',
        alpha=0.8)

plt.show()
