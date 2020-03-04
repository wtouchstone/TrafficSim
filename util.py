import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
import copy
def aStarHeuristic(graph, source, dest):
    return 110996.4513 * pow(pow((graph.nodes[source]['x'] - graph.nodes[dest]['x']),2) + pow((graph.nodes[source]['y'] - graph.nodes[dest]['y']),2),.5) #meters times lattitude at 38 degrees

def closestNode(graph, location): #tuple location
    return ox.geo_utils.get_nearest_node(graph, location)

def cost(G, edge):
    return ox.geo_utils.get_route_edge_attributes(G, edge)[0]['length']


def gmlAStar(graph, source, dest): #NODE source, NODE dest, returns a path (list of node) from source to dest.
    #explorable = PriorityQueue()
    if (source == dest):
        return []
    successors = graph.edges(source)
    openQueue = []
    visitedSet = set()
    finalDest = 0
    for successor in successors:
        heuristic = aStarHeuristic(graph, successor[1], dest)
        currCost = cost(graph, successor)
        history = [source]
        totalCost = currCost + heuristic + 0
        heapq.heappush(openQueue, (totalCost, successor[1], history, currCost))
    print(openQueue)
    while openQueue:    
        curr = heapq.heappop(openQueue)
        print(curr)
        if curr[1] not in visitedSet:
            visitedSet.add(curr[1])
            if curr[1] == dest:
                curr[2].append(curr[1])
                return curr[2]
            successors = graph.edges(curr[1])
            for successor in successors:
                heuristic = aStarHeuristic(graph, successor[1], dest)
                currCost = cost(graph, successor) + curr[3]
                history = copy.deepcopy(curr[2])
                history.append(curr[1])
                totalCost = currCost + curr[3] + heuristic
                heapq.heappush(openQueue, (totalCost, successor[1], history, currCost))
    #path = unpackPath(finalDest)
    return finalDest[2]
