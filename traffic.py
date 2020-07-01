import osmnx as ox
import networkx as nx
import xml.dom.minidom
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure 
import matplotlib.animation as animation 
from util import *
from pprint import pprint

import tkinter as tk
from tkinter import ttk

matplotlib.use("TkAgg")


ox.utils.config(all_oneway=False)
G = ox.graph_from_place("ball ground, ga", buffer_dist=0, network_type='drive')
for edge in G.edges(keys=True, data=True):
    edge[3]['traversals'] = 0


#G, fig, ax = run_sim_and_graph(G, dpi=1000, num_iters=10, save=False, filename="traffic", edge_linewidth=1, show_congestion=False, draw_freq=1)
LARGE_FONT= ("Verdana", 12)




class TrafficSim(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Traffic Simulator")
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

      

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

      
class StartPage(tk.Frame):
    G = None
    scale = None
    fig = None
    canvas = None
    cumulative_iters = 0
    def initialize_graph_window(self):
        self.G = ox.graph_from_place("davisboro, ga", network_type='drive') #create graph window, fill with nothing
        for edge in self.G.edges(keys=True, data=True):
            edge[3]['traversals'] = 0
        self.G, self.fig, self.ax = run_sim_and_graph(self.G, num_iters=0)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=7)    
    
    def initialize_graph(self, location):
        self.G = ox.graph_from_place(location, buffer_dist=0, network_type='drive')
        for edge in self.G.edges(keys=True, data=True):
            edge[3]['traversals'] = 0
        #self.G, temp1, temp2 = run_sim_and_graph(self.G, num_iters=0)
        print("Fetched %s successfully", location)
        axes = plt.gca()
        plt.ion()
        redraw_axes(self.G, axes, 0)
        plt.ioff()
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=7)

    def graph(self, iters):
        ox.utils.config(all_oneway=False)
        for i in range(iters):
            simulate_random(self.G)
        axes = plt.gca()
        plt.ion()
        self.cumulative_iters += iters
        update_axes(self.G, axes, self.cumulative_iters)
        plt.ioff()
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=7)
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.grid(row=0, pady=10,padx=10, column=1)
        self.initialize_graph_window()

        scale = ttk.Scale(self, from_=2, to=500, value=True)
        location_tf = ttk.Entry(self)
        button_fetch = ttk.Button(self, text="Fetch", command=lambda: self.initialize_graph(location_tf.get()))
        button_simulate = ttk.Button(self, text="Simulate", command=lambda: self.graph(int(scale.get())))
        button_save = ttk.Button(self, text="Save Image")

        location_tf.grid(row=1,column=1)
        button_fetch.grid(row=1,column=2)
        button_simulate.grid(row=2,column=2)
        scale.grid(row=3, column=1)
        button_save.grid(row=7, column=0)



        








app = TrafficSim()
app.mainloop()
#ani = animation.FuncAnimation(ax, animate, interval=1000)





#ox.save_load.save_as_osm(G, filename="techdrive.osm")
#G = ox.graph_from_file("./data/techdrive.osm")
#ox.elevation.add_edge_grades(G)
#pprint(basic_stats)
#ox.plot_graph(G)
edgeDict = {}




node = np.random.choice(G.nodes)





