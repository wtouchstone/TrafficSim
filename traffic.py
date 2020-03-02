import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
from util import *
from pprint import pprint
G = ox.graph_from_address("301 10th St NW, Atlanta, GA", distance = 700)
#ox.elevation.add_edge_grades(G)
basic_stats = ox.basic_stats(G)
#pprint(basic_stats)
#ox.plot_graph(G)

def gmlAStar(graph, source, dest): #NODE source, NODE dest
    #explorable = PriorityQueue()
    if (source == dest):
        return []
    successors = graph.edges(source)
    openQueue = []
    visitedSet = set()
    finalDest = 0
    for successor in successors:
        heuristic = aStarHeuristic(G, successor[1], dest)
        currCost = cost(G, successor)
        parent = (0, source, list())
        totalCost = currCost + parent[0] + heuristic
        heapq.heappush(openQueue, (totalCost, successor[1], parent))
    while openQueue:
        #print("orig")
        #print(source)
        #print("dest")
        #print(dest)
        #print(openQueue[0][1])
        curr = heapq.heappop(openQueue)
        if curr[1] not in visitedSet:
            visitedSet.add(curr[1])
            if curr[1] == dest:
                #print (curr)
                finalDest = curr
                break
            successors = graph.edges(curr[1])
            for successor in successors:
                heuristic = aStarHeuristic(G, successor[1], dest)
                currCost = cost(G, successor)
                parent = curr
                totalCost = currCost + parent[0] + heuristic
                heapq.heappush(openQueue, (totalCost, successor[1], parent))
    print(finalDest)
    path = unpackPath(finalDest)
    return path
    
    
    
        
    

    #print(successors)
    #node is (cumulative cost, id, list of parents)
    #while False:
    #    adjacent = graph.edges(source)

#print(closestNode(G, (33.779609,-84.4061026)))
#print(ox.geo_utils.get_nearest_edges(G, [33.779609],[-84.4061026], dist = 100))
ox.save_load.save_graphml(G, filename='graph.graphml')
node1 = np.random.choice(G.nodes)
node2 = np.random.choice(G.nodes)
path = gmlAStar(G, node1, node2)
ox.plot_graph_route(G, path)
node1 = np.random.choice(G.nodes)
node2 = np.random.choice(G.nodes)
path = gmlAStar(G, node1, node2)
ox.plot_graph_route(G, path)
node1 = np.random.choice(G.nodes)
node2 = np.random.choice(G.nodes)
path = gmlAStar(G, node1, node2)
ox.plot_graph_route(G, path)
#ox.plot_graph(G)
#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))
#print(type(thing[0][0]))


node = np.random.choice(G.nodes)





