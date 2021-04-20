from kivy.garden.graph import MeshLinePlot
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from math import sin

import matplotlib
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from graph_formating import plot_text, plot_line_graph, plot_bar_graph

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__()

    def start(self):
        #self.ids.graph.add_plot(self.plot) #same result if this line is added here
        for i in range(25):
            data_to_graph = [(x, sin(x)+ i) for x in range(0, 101)] #apply a DC offset to each trace to display multiple traces
            print(data_to_graph)
            self.plot = MeshLinePlot(color=[.5, .5, 1, 1])
            self.plot.points = data_to_graph
            self.ids.graph.add_plot(self.plot)

class GraphDemo(App):
    def build(self):
        return Builder.load_file("output.kv")

if __name__ == "__main__":
    GraphDemo().run()