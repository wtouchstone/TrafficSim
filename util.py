import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
def aStarHeuristic(graph, source, dest):
    return 110996.4513 * pow(pow((graph.nodes[source]['x'] - graph.nodes[dest]['x']),2) + pow((graph.nodes[source]['y'] - graph.nodes[dest]['y']),2),.5) #meters times lattitude at 38 degrees

def closestNode(graph, location): #tuple location
    return ox.geo_utils.get_nearest_node(graph, location)

def cost(G, edge):
    return ox.geo_utils.get_route_edge_attributes(G, edge)[0]['length']

def unpackPath(node):
    nodeList = list()
    while node[2]:
        nodeList.append(node[1])
        node = node[2]
    nodeList.reverse()
    return nodeList
