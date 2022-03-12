import pandas as pd
import networkx as nx
import json
from networkx.readwrite import json_graph

df = pd.read_csv('https://raw.githubusercontent.com/umassdgithub/Week-7-ForceLayout/main/data/data_scopus.csv')

df['Publisher'] = df['Publisher'].fillna('Unknown')
publisher_names = set(df['Publisher'].values)

publisher_num_papers = df.groupby('Publisher').agg(count_col=pd.NamedAgg(column='Publisher', aggfunc="count"))

publisher_num = 1
publishers = []
for publisher_name in publisher_names:
    if publisher_name != 'Unknown':
        publisher_size = 1
        if publisher_name in publisher_num_papers.index:
            publisher_size = int(publisher_num_papers.loc[publisher_name]['count_col'])

        publishers.append((publisher_num, {"name": publisher_name, "size": publisher_size}))
        publisher_num += 1

edged = {}
for row in df.iterrows():
    current_paper = row[1]
    if ";" in current_paper['Author(s) ID'] and current_paper['Publisher'] != 'Unknown': 
        authors = current_paper['Author(s) ID'][:-1].split(";")

        for author in authors:
            other_papers_pubs = df[df['Author(s) ID'].str.contains(author)]['Publisher'].values
            if len(other_papers_pubs) > 0:
                for other_paper_pub in other_papers_pubs:
                    if other_paper_pub != current_paper['Publisher'] and other_paper_pub != 'Unknown':
                        this_publisher_index = next(x for x in publishers if x[1]['name'] == current_paper['Publisher'])[0]
                        other_publisher_index = next(x for x in publishers if x[1]['name'] == other_paper_pub)[0]
                        if (this_publisher_index, other_publisher_index) in edged:
                            edge = edged.get((this_publisher_index, other_publisher_index))
                            edge[2]['weight'] += 1
                        else:
                            edged[(this_publisher_index, other_publisher_index)] = (this_publisher_index, other_publisher_index, {"weight": 1})
    else:
        continue

edges = edged.values()

G = nx.Graph()
G.add_nodes_from(publishers)
G.add_edges_from(edges)

with open("publisher_network.json",'w') as f:
      json.dump(json_graph.node_link_data(G),f)

