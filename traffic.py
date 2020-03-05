import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import pandas as pd
from util import *  
from pprint import pprint
ox.utils.config(all_oneway=False)
G = ox.graph_from_place("Atlanta", network_type='drive')
#G = ox.graph_from_file("./data/map.osm", netwo)
#ox.elevation.add_edge_grades(G)
#pprint(basic_stats)
#ox.plot_graph(G)
edgeDict = {}

#print(ox.geo_utils.get_nearest_edges(G, [33.779609],[-84.4061026], dist = 100))
#ox.save_load.save_as_osm(G, filename='tech.osm', oneway=True)
for edge in G.edges(keys=True, data=True):
    edge[3]['traversals'] = 0
maxTraversals = 0
for i in range(10000):
    node1 = np.random.choice(G.nodes)
    node2 = np.random.choice(G.nodes)
    path = gmlAStar(G, node1, node2)

    if path != []:
        for j in range(1,len(path)):
            edge = (path[j-1], path[j])
            ox.geo_utils.get_route_edge_attributes(G, edge)[0]['traversals'] += 1
            if ox.geo_utils.get_route_edge_attributes(G, edge)[0]['traversals'] > maxTraversals:
                maxTraversals = ox.geo_utils.get_route_edge_attributes(G, edge)[0]['traversals']
#for edge in G.edges(keys=True, data=True):
    #edge[3]['traversals'] /= maxTraversals
    #print(edge[3]['traversals'])
edgeattrs = ox.graph_to_gdfs(G, nodes=False).columns
#beep = ox.plot.get_edge_colors_by_attr(G, 'traversals', num_bins=5)
beep = get_edge_colors_by_attribute(G, 'traversals', num_bins=250)
ox.plot_graph(G, edge_color=beep, node_alpha=0, bgcolor='grey', edge_linewidth=4)
#ox.plot_graph_route(G, path)
#print(edgeDict)


#ox.plot_graph(G)
#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))
#print(type(thing[0][0]))


node = np.random.choice(G.nodes)





