import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import heapq
import copy
import pandas as pd
import time

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from osmnx import settings
from osmnx.core import graph_from_address
from osmnx.core import graph_from_point
from osmnx.core import bbox_from_point
from osmnx.projection import project_graph
from osmnx.save_load import graph_to_gdfs
from osmnx.simplify import simplify_graph
from osmnx.utils import log
from matplotlib.collections import LineCollection
from descartes import PolygonPatch
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from osmnx.plot import save_and_show
import math as m


def aStarHeuristic(graph, source, dest):
    # This heuristic is strictly a euclidian distance heuristic. It's probably not technically
    # admissible and it's definitely not consistent, as the cost for two pairs of nodes
    # that are equidistant can change based on the speed limit, whereas the heuristic would 
    # return the same thing. I would consider this a problem, but I'll attribute it to
    # ~realistic accuracy~ of people not always choosing the exact optimal route, so I elect
    # to not care.
    return (1/35.0) * 110996.4513 * pow(pow((graph.nodes[source]['x'] - graph.nodes[dest]['x']),2) + pow((graph.nodes[source]['y'] - graph.nodes[dest]['y']),2),.5) #meters times lattitude at 38 degrees


def closestNode(graph, location): #tuple location
    # Determines the closest node to a given node.
    return ox.geo_utils.get_nearest_node(graph, location)


def cost(G, edge):
    # This cost function takes the distance and divides by the speed limit of the road, 
    # essentially making the cost of the edge time based.
    distance = ox.geo_utils.get_route_edge_attributes(G, edge)[0]['length']
    try:
        speedLimit = ox.geo_utils.get_route_edge_attributes(G, edge)[0]['maxspeed']
        speedLimit = int(speedLimit[0:2])
    except:
        speedLimit = 35
    cost = distance/speedLimit
    return cost


def gmlAStar(graph, source, dest): #NODE source, NODE dest, returns a path (list of node) from source to dest.
    # This function uses A* Search to find the optimal path given a cost function, using a heuristic
    # to narrow down the search for the optimal path. Heurestic and cost defined above.
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

def get_edge_colors_by_attribute(G, attr, num_bins=5, cmap='viridis', start=0, stop=1, na_color='none'): 
    # This is a modified version of that of osmnx with corrected buckets for my purposes.
    # It iterates through the edges and assigns them colors based on a given attribute. 
    if num_bins is None:
            num_bins=len(G.edges())
    bin_labels = range(num_bins)
    attr_values = pd.Series([m.log(data[attr] + 1,10) for u, v, key, data in G.edges(keys=True, data=True)])
    cats = pd.cut(x=attr_values, bins=num_bins, labels=bin_labels)
    colors = ox.plot.get_colors(num_bins, cmap, start, stop)
    edge_colors = [colors[int(cat)] if pd.notnull(cat) else na_color for cat in cats]
    return edge_colors


def get_edge_colors_by_attribute_edges(edges, attr, num_bins=5, cmap='viridis', start=0, stop=1, na_color='none'): 
    # This function is similar to the one above, except it only takes in the edges.
    # Returns similarly to above.
    if num_bins is None:
            num_bins=len(edges)
    bin_labels = range(num_bins)
    attr_values = pd.Series([data[attr] for u, v, data in edges])
    cats = pd.cut(x=attr_values, bins=num_bins, labels=bin_labels)
    colors = ox.plot.get_colors(num_bins, cmap, start, stop)
    edge_colors = [colors[int(cat)] if pd.notnull(cat) else na_color for cat in cats]
    return edge_colors


def simulate_random(G):
    # This function will simulate a random path between two random nodes. The random nodes 
    # have a indirect correlation population density as more intersections likely means
    # more people. If there were a good API I could find, I would like to be more realistic
    # sampling by using zoning and population density.
    node1 = np.random.choice(G.nodes)
    node2 = np.random.choice(G.nodes)
    path = gmlAStar(G, node1, node2)
    if path != []:
        for j in range(1,len(path)):
            edge = (path[j-1], path[j])
            ox.geo_utils.get_route_edge_attributes(G, edge)[0]['traversals'] += 1
    return path


def eval_congestion(G): #TODO: create more advanced congestion evaluation
    # This function will produce a new edge attribute called "congestion".
    # This attribute represents a rudimentary representation of what a person
    # actually experiences on a road. If I didn't want to hurry up and be done
    # with this project to move on to other things, I would do some research
    # on producing a more accurate formula.
    for edge in G.edges(keys=True, data=True):
        num_lanes = 1
        try:
            num_lanes = int(edge[3]['lanes'])
        except:
            num_lanes = 1
        try:
            speed_lim = int(edge[3]['maxspeed'])
        except:
            speed_lim = 35

        edge[3]['congestion'] = edge[3]['traversals'] / num_lanes
        edge[3]['avgspeed'] = edge[3]['congestion'] * speed_lim


def redraw_axes(G, axes,  num_iters):
    # This function will redraw the axes when a new location has been fetched. Similar
    # in behavior to later "update_axes".
    # This function replots the view after the road network has been updated. 
    # params: G:              road network graph
    #         axes:           matplotlib axes for plot
    #         num_iters:      number of iterations simulated since last update, to update count at top
    #         congestion:     whether or not to graph in congestion mode (alternative is volume)
    axes.collections[0].remove()
    lines = []
    edges = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
    west, south, east, north = edges.total_bounds
    axes.set_ylim((south, north))
    axes.set_xlim((west, east))
    for u, v, data in G.edges(keys=False, data=True):
        if 'geometry' in data and True:
            # if it has a geometry attribute (a list of line segments), add them
            # to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute, the edge is a straight
            # line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)

    eColors = get_edge_colors_by_attribute(G, 'traversals', num_bins=5)
    widths = calc_width_from_colors(eColors, 3, calc_size_weight(north, south)) 
    lc = LineCollection(lines, colors=eColors, linewidths=widths, zorder=2)
    axes.set_title(num_iters)
    axes.add_collection(lc)


def calc_width_from_colors(colors, weight, sizeweight):
    # This function will calculate the width of the lines to be graphed. Because
    # the viridis color spectrum maintains a linear increase in luminance
    # with larger values, these calculations can be solely based on luminance 
    # as it has a direct correlation with the value being graphed.
    widths = list()
    for i in range(len(colors)):
        r, g, b = colors[i][0], colors[i][1], colors[i][2]
        luminance = (0.2126*r + 0.7152*g + 0.0722*b) #found this bad boy on stackoverflow
        luminancenorm = (luminance - 0.084) * 1.273
        alpha = luminancenorm * 2
        if (alpha < 0.3):
            colors[i] = (colors[i][0], colors[i][1], colors[i][2], 0.3)
        elif (alpha > 1):
            colors[i] = (colors[i][0], colors[i][1], colors[i][2], 1)
        else:
            colors[i] = (colors[i][0], colors[i][1], colors[i][2], alpha) #have to account for imprecision
        widths.append(luminance * weight * sizeweight + .1)
    return widths




def calc_size_weight(north, south): #result is smaller for larger area
    # This function will calculate the increased/decreased weight based on
    # the size of the area being graphed. This is so large areas will not 
    # have very wide and insdistinguishible road lines. Uses 10th root to
    # make sure large graphs do not eventually get paper thin lines.
    height = abs(north - south)
    root_height = pow(height, 1/10)
    scalar = 0.5
    weight = pow(root_height, -1) * scalar
    return weight


def update_axes(G, axes,  num_iters, congestion):
    # This function replots the view after the road network has been updated. 
    # params: G:              road network graph
    #         axes:           matplotlib axes for plot
    #         num_iters:      number of iterations simulated since last update, to update count at top
    #         congestion:     whether or not to graph in congestion mode (alternative is volume)
    axes.collections[0].remove()
    lines = []
    west, south, east, north = (ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)).total_bounds
    sortededges = sorted(G.edges(keys=False, data=True), key=lambda t: t[2].get('avgspeed', 1))
    for u, v, data in sortededges:
        if 'geometry' in data and True:
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)
    if congestion:
        eval_congestion(G)
        eColors = get_edge_colors_by_attribute_edges(sortededges, 'avgspeed', num_bins=5)
    else:
        eColors = get_edge_colors_by_attribute_edges(sortededges, 'traversals', num_bins=5)
    widths = calc_width_from_colors(eColors, 3, calc_size_weight(north, south))    
    lc = LineCollection(lines, colors=eColors, linewidths=widths, zorder=2)
    axes.set_title(num_iters)
    axes.add_collection(lc)

    


def run_sim_and_graph(G, bbox=None, fig_height=6, fig_width=None, margin=0.02,
               axis_off=True, equal_aspect=False, bgcolor='w', show=True,
               save=False, close=True, file_format='png', filename='temp',
               dpi=600, annotate=False, node_color='#66ccff', node_size=15,
               node_alpha=1, node_edgecolor='none', node_zorder=1,
               edge_color='#999999', edge_linewidth=1, edge_alpha=1, prior_iters=0,
               use_geom=True, num_iters=20, draw_freq=50, show_congestion=False):
    # This is mostly lifted directedly from osmnx. Using it to enable real time graphing as more 
    # samples are taken
    """
    Plot a networkx spatial graph.
    Parameters, 
    ----------
    G : networkx multidigraph
    bbox : tuple
        bounding box as north,south,east,west - if None will calculate from
        spatial extents of data. if passing a bbox, you probably also want to
        pass margin=0 to constrain it.
    fig_height : int
        matplotlib figure height in inches
    fig_width : int
        matplotlib figure width in inches
    margin : float
        relative margin around the figure
    axis_off : bool
        if True turn off the matplotlib axis
    equal_aspect : bool
        if True set the axis aspect ratio equal
    bgcolor : string
        the background color of the figure and axis
    show : bool
        if True, show the figure
    save : bool
        if True, save the figure as an image file to disk
    close : bool
        close the figure (only if show equals False) to prevent display
    file_format : string
        the format of the file to save (e.g., 'jpg', 'png', 'svg')
    filename : string
        the name of the file if saving
    dpi : int
        the resolution of the image file if saving
    annotate : bool
        if True, annotate the nodes in the figure
    node_color : string
        the color of the nodes
    node_size : int
        the size of the nodes
    node_alpha : float
        the opacity of the nodes
    node_edgecolor : string
        the color of the node's marker's border
    node_zorder : int
        zorder to plot nodes, edges are always 2, so make node_zorder 1 to plot
        nodes beneath them or 3 to plot nodes atop them
    edge_color : string
        the color of the edges' lines
    edge_linewidth : float
        the width of the edges' lines
    edge_alpha : float
        the opacity of the edges' lines
    use_geom : bool
        if True, use the spatial geometry attribute of the edges to draw
        geographically accurate edges, rather than just lines straight from node
        to node
    Returns
    -------
    fig, ax : tuple
    """

    log('Begin plotting the graph...')
    node_Xs = [float(x) for _, x in G.nodes(data='x')]
    node_Ys = [float(y) for _, y in G.nodes(data='y')]
    # get north, south, east, west values either from bbox parameter or from the
    # spatial extent of the edges' geometries
    if bbox is None:
        edges = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
        west, south, east, north = edges.total_bounds
    else:
        north, south, east, west = bbox

    # if caller did not pass in a fig_width, calculate it proportionately from
    # the fig_height and bounding box aspect ratio
    bbox_aspect_ratio = (north-south)/(east-west)
    if fig_width is None:
        fig_width = fig_height / bbox_aspect_ratio

    # create the figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor=bgcolor)
    ax.set_facecolor(bgcolor)

    # draw the edges as lines from node to node
    start_time = time.time()
    lines = []
    for u, v, data in G.edges(keys=False, data=True):
        if 'geometry' in data and use_geom:
            # if it has a geometry attribute (a list of line segments), add them
            # to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute, the edge is a straight
            # line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)

    # add the lines to the axis as a linecollection
    
    
    log('Drew the graph edges in {:,.2f} seconds'.format(time.time()-start_time))
    # scatter plot the nodes
    #ax.scatter(node_Xs, node_Ys, s=node_size, c=node_color, alpha=node_alpha, edgecolor=node_edgecolor, zorder=node_zorder)

    # set the extent of the figure

    margin_ns = (north - south) * margin
    margin_ew = (east - west) * margin
    ax.set_ylim((south - margin_ns, north + margin_ns))
    ax.set_xlim((west - margin_ew, east + margin_ew))

    # configure axis appearance
    xaxis = ax.get_xaxis()
    yaxis = ax.get_yaxis()

    xaxis.get_major_formatter().set_useOffset(False)
    yaxis.get_major_formatter().set_useOffset(False)

    #eColors = get_edge_colors_by_attribute(G, 'traversals', num_bins=250)
    #lc = LineCollection(lines, colors=eColors, linewidths=edge_linewidth, alpha=edge_alpha, zorder=2)
    #ax.add_collection(lc)
    
    #plt.pause(2)
    #plt.ion()


    for i in range(1, num_iters+1):
        simulate_random(G)
       # if (i % draw_freq == 0 or i == num_iters):
    plt.cla()
    ax.set_facecolor = bgcolor
    ax.set_ylim((south - margin_ns, north + margin_ns))
    ax.set_xlim((west - margin_ew, east + margin_ew))
    xaxis.get_major_formatter().set_useOffset(False)
    yaxis.get_major_formatter().set_useOffset(False)
    ax.set_title(num_iters + prior_iters)
    ax.set_aspect('equal')
    ax.axis('off')
    if (show_congestion):
        eval_congestion(G)
        eColors = get_edge_colors_by_attribute(G, 'congestion', num_bins=250)
    else:
        eColors = get_edge_colors_by_attribute(G, 'traversals', num_bins=250)
    lc = LineCollection(lines, colors=eColors, linewidths=edge_linewidth, alpha=edge_alpha, zorder=2)
    ax.add_collection(lc)
    #plt.pause(0.000001)

    #plt.ioff()
    
    #ax.add_collection(lc)
    
    # if axis_off, turn off the axis display set the margins to zero and point
    # the ticks in so there's no space around the plot
    if axis_off:
        ax.axis('off')
        ax.margins(0)
        ax.tick_params(which='both', direction='in')
        xaxis.set_visible(False)
        yaxis.set_visible(False)
        #fig.canvas.draw()

    if equal_aspect:
        # make everything square
        ax.set_aspect('equal')
        #fig.canvas.draw()
    else:
        # if the graph is not projected, conform the aspect ratio to not stretch the plot
        if G.graph['crs'] == settings.default_crs:
            coslat = np.cos((min(node_Ys) + max(node_Ys)) / 2. / 180. * np.pi)
            ax.set_aspect(1. / coslat)
            #fig.canvas.draw()

    # annotate the axis with node IDs if annotate=True
    if annotate:
        for node, data in G.nodes(data=True):
            ax.annotate(node, xy=(data['x'], data['y']))

    # save and show the figure as specified
    if save == True:
        #fig.canvas.draw()
        fig, ax = save_and_show(fig, ax, save, show, close, filename, file_format, dpi, axis_off)
    ##fig.canvas.draw()
    #fig.canvas.flush_events()
    return G, fig, ax