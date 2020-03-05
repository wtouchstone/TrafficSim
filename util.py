import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
import copy
import pandas as pd
def aStarHeuristic(graph, source, dest):
    return (1/35.0) * 110996.4513 * pow(pow((graph.nodes[source]['x'] - graph.nodes[dest]['x']),2) + pow((graph.nodes[source]['y'] - graph.nodes[dest]['y']),2),.5) #meters times lattitude at 38 degrees

def closestNode(graph, location): #tuple location
    return ox.geo_utils.get_nearest_node(graph, location)

def cost(G, edge):
    distance = ox.geo_utils.get_route_edge_attributes(G, edge)[0]['length']
    try:
        speedLimit = ox.geo_utils.get_route_edge_attributes(G, edge)[0]['maxspeed']
        speedLimit = int(speedLimit[0:2])
    except:
        speedLimit = 35
    cost = distance/speedLimit
    return cost


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
    while openQueue:    
        curr = heapq.heappop(openQueue)
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
    try:
        return finalDest[2]
    except:
        return[]
#this is a modified version of that of osmnx with corrected buckets for my purposes
def get_edge_colors_by_attribute(G, attr, num_bins=5, cmap='viridis', start=0, stop=1, na_color='none'): 
    if num_bins is None:
            num_bins=len(G.edges())
    bin_labels = range(num_bins)
    attr_values = pd.Series([data[attr] for u, v, key, data in G.edges(keys=True, data=True)])
    cats = pd.cut(x=attr_values, bins=num_bins, labels=bin_labels)
    #cats = []
    #for i in range(num_bins + 1):
    #    cats.append(float(i) / num_bins)
    colors = ox.plot.get_colors(num_bins, cmap, start, stop)
    edge_colors = [colors[int(cat)] if pd.notnull(cat) else na_color for cat in cats]
    return edge_colors
