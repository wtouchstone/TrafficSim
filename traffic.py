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
LARGE_FONT= ("Verdana", 12)




class TrafficSim(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Traffic Simulator")
        tk.Tk.iconbitmap(self,default='resources/icon.ico')
        
        
        container = ttk.Frame(self)
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
    congestion = False
   

    def get_graph_size(self):
        west, south, east, north = (ox.graph_to_gdfs(self.G, nodes=False, fill_edge_geometry=True)).total_bounds
        return abs(north - south)

    def initialize_graph_window(self):
        self.G = ox.graph_from_place("davisboro, ga", network_type='drive') #create graph window, fill with nothing
        for edge in self.G.edges(keys=True, data=True):
            edge[3]['traversals'] = 0
        self.G, self.fig, self.ax = run_sim_and_graph(self.G, num_iters=0)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=25)    
    
    def initialize_graph(self, location, buffer_distance):
        self.cumulative_iters = 0
        self.status_text.set("Fetching, please wait...")
        self.update()
        self.G = ox.graph_from_place(location, buffer_dist=buffer_distance, network_type='drive')
        self.status_text.set("Done fetching. Graphing...")
        self.update()
        for edge in self.G.edges(keys=True, data=True):
            edge[3]['traversals'] = 0
        axes = plt.gca()
        plt.ion()
        redraw_axes(self.G, axes, 0)
        update_axes(self.G, axes, self.cumulative_iters, self.congestion)
        plt.ioff()
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=25)
        self.status_text.set("Finished graphing.")

    def graph(self, iters):
        ox.utils.config(all_oneway=False)
        for i in range(iters):
            self.update()
            self.status_text.set("Simulating iteration #" + str(i))
            simulate_random(self.G)
        axes = plt.gca()
        plt.ion()
        self.status_text.set("Simulation completed, updating plot.")
        self.update()
        self.cumulative_iters += iters
        update_axes(self.G, axes, self.cumulative_iters, self.congestion)
        plt.ioff()
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, rowspan=25)
        self.status_text.set("Plot update completed.")


    def update_iter_label(self, value):
        self.iter_val.set(int(float(value)))

    def flip_congestion(self):
        if self.congestion:
            self.congestion = False
            self.congestion_text.set("Switch to Congestion View")
            self.graph(0)
        else:
            self.congestion = True
            self.congestion_text.set("Switch to Volume View")
            self.graph(0)





    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Traffic Congestion Simulator", font=LARGE_FONT)
        label.grid(row=0, pady=10,padx=10, column=1, columnspan=3)
        self.initialize_graph_window()
        self.iter_val = tk.StringVar()
        self.iter_val.set("0")
        self.status_text = tk.StringVar()
        self.congestion_text = tk.StringVar()
        self.congestion_text.set("Switch to Congestion View")

        v1 = tk.IntVar()
        location_tf = ttk.Entry(self)
        buffer_dist_tf = ttk.Entry(self)
        buffer_dist_tf.insert(0, "0")
        button_fetch = ttk.Button(self, text="Fetch", command=lambda: self.initialize_graph(location_tf.get(), float(buffer_dist_tf.get())))
        button_simulate = tk.Button(self, text="Simulate", command=lambda: self.graph(int(scale.get())), width=15, height=2)
        button_save = ttk.Button(self, text="Save Image", command=lambda: plt.savefig("result.png", dpi=3000 * self.get_graph_size()))
        button_congestion = ttk.Button(self, textvariable=self.congestion_text, command=lambda: self.flip_congestion())
        iteration_label = ttk.Label(self, textvariable=self.iter_val)
        status_label = ttk.Label(self, textvariable=self.status_text)
        num_iters_label = ttk.Label(self, text="Number of iterations to simulate:", anchor=tk.W)
        buffer_dist_label = ttk.Label(self, text="Buffer distance (m)")
        fetch_location_label = ttk.Label(self, text="Fetch a new location:")

        scale = ttk.Scale(self, from_=1.1, to=500, value=True, variable=v1, command=self.update_iter_label, length=175)

        fetch_location_label.grid(row=1, column=1)
        location_tf.grid(row=2,column=1, columnspan=2)
        button_fetch.grid(row=2,column=3)
        buffer_dist_tf.grid(row=3,column=1, columnspan=2)
        buffer_dist_label.grid(row=3,column=3)
        num_iters_label.grid(row=4, column=1, columnspan=2)
        scale.grid(row=5, column=1, columnspan=2)
        iteration_label.grid(row=5, column=3)
        button_simulate.grid(row=7,column=1, columnspan=3)
        button_congestion.grid(row=24, column=1, columnspan=3)
        button_save.grid(row=25, column=0)
        status_label.grid(row=25, column=1)

        



app = TrafficSim()
app.mainloop()



