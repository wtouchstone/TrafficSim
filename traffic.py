import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
from util import *
from pprint import pprint
G = ox.graph_from_place("Georgia Institute of Technology")
#ox.elevation.add_edge_grades(G)
basic_stats = ox.basic_stats(G)
#pprint(basic_stats)


def gmlAStar(graph, source, dest): #NODE source, NODE dest
    #explorable = PriorityQueue()
    if (source == dest):
        return []
    successors = graph.edges(source)
    openQueue = []
    for successor in successors:
        print(successor)
        #cost = successor.length + 
        #heapq.heappush(openQueue, )
    #print(successors)
    #node is (cumulative cost, id, list of parents)
    #while False:
    #    adjacent = graph.edges(source)

#print(closestNode(G, (33.779609,-84.4061026)))
#print(ox.geo_utils.get_nearest_edges(G, [33.779609],[-84.4061026], dist = 100))
ox.save_load.save_graphml(G, filename='graph.graphml')
gmlAStar(G, closestNode(G, (33.779609,-84.4061026)), closestNode(G, (90.779609,90.4061026)))
#ox.plot_graph(G)
#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))
#print(type(thing[0][0]))
#ox.plot_graph_route(G, route)
node = np.random.choice(G.nodes)





print(aStarHeuristic(G,69222787,69222790))

