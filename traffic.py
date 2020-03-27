import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import *  
from pprint import pprint




ox.utils.config(all_oneway=False)
G = ox.graph_from_place("los angeles, ca", buffer_dist=0, network_type='drive')
#ox.save_load.save_as_osm(G, filename="techdrive.osm")
#G = ox.graph_from_file("./data/techdrive.osm")
#ox.elevation.add_edge_grades(G)
#pprint(basic_stats)
#ox.plot_graph(G)
edgeDict = {}

#print(ox.geo_utils.get_nearest_edges(G, [33.779609],[-84.4061026], dist = 100))
#ox.save_load.save_as_osm(G, filename='tech.osm', oneway=True)
for edge in G.edges(keys=True, data=True):
    edge[3]['traversals'] = 0
maxTraversals = 0
beep = None
#for i in range(20):
#    simulate_random(G)
    #node1 = np.random.choice(G.nodes)
    #node2 = np.random.choice(G.nodes)
    #path = gmlAStar(G, node1, node2)

    #if path != []:
    #    for j in range(1,len(path)):
    #        ox.geo_utils.get_route_edge_attributes(G, (path[j-1], path[j]))[0]['traversals'] += 1
            #G.edges[(path[j-1], path[j])] += 1
            
#beep = get_edge_colors_by_attribute(G, 'traversals', num_bins=250)
#ox.plot_graph(G, edge_color=beep, node_alpha=0, bgcolor='grey', save=False, file_format='png', dpi=2000, edge_linewidth=1)
    #plt.pause(0.1)
#fig.show()

#plt.show()

#ox.plot_graph_route(G, simulate_random(G))

run_sim_and_graph(G, bgcolor='grey', dpi=1000, num_iters=5)



#ox.plot_graph(G)
#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))
#print(type(thing[0][0]))


node = np.random.choice(G.nodes)





