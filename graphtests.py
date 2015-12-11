# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

g = nx.watts_strogatz_graph(53, 4,  .3);
nx.draw_spring(wgraph)