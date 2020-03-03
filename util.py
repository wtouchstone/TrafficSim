import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
def aStarHeuristic(graph, source, dest):
    return 110996.4513 * pow(pow((graph.nodes[source]['x'] - graph.nodes[dest]['x']),2) + pow((graph.nodes[source]['y'] - graph.nodes[dest]['y']),2),.5) #meters times lattitude at 38 degrees

def closestNode(graph, location): #tuple location
    return ox.geo_utils.get_nearest_node(graph, location)

def cost(G, edge):
    return ox.geo_utils.get_route_edge_attributes(G, edge)[0]['length']

def unpackPath(node):
    nodeList = list()
    try:
        while node[2]:
            nodeList.append(node[1])
            node = node[2]
    except:
        print(node)
    nodeList.reverse()
    return nodeList

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
        parent = (0, source, list())
        totalCost = currCost + parent[0] + heuristic
        heapq.heappush(openQueue, (totalCost, successor[1], parent))
    while openQueue:
        curr = heapq.heappop(openQueue)
        if curr[1] not in visitedSet:
            visitedSet.add(curr[1])
            if curr[1] == dest:
                finalDest = curr
                break
            successors = graph.edges(curr[1])
            for successor in successors:
                heuristic = aStarHeuristic(graph, successor[1], dest)
                currCost = cost(graph, successor)
                parent = curr
                totalCost = currCost + parent[0] + heuristic
                heapq.heappush(openQueue, (totalCost, successor[1], parent))
    path = unpackPath(finalDest)
    return path
