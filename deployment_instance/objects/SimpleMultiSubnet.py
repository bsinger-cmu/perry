import networkx as nx


class Topology:

    def __init__(self, name : str):
        self.name = name
        self.graph = nx.Graph()

    