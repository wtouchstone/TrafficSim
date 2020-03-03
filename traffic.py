import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
from util import *  
from pprint import pprint
ox.utils.config(all_oneway=False)
G = ox.graph_from_place("Ball Ground, GA", buffer_dist=500, network_type='drive')
#ox.elevation.add_edge_grades(G)
basic_stats = ox.basic_stats(G)
#pprint(basic_stats)
#ox.plot_graph(G)


#print(closestNode(G, (33.779609,-84.4061026)))
#print(ox.geo_utils.get_nearest_edges(G, [33.779609],[-84.4061026], dist = 100))
#ox.save_load.save_as_osm(G, filename='tech.osm', oneway=True)
for i in range(10):
    node1 = np.random.choice(G.nodes)
    node2 = np.random.choice(G.nodes)
    path = gmlAStar(G, node1, node2)
    if path != []:
        ox.plot_graph_route(G, path)

#ox.plot_graph(G)
#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))
#print(type(thing[0][0]))


node = np.random.choice(G.nodes)





