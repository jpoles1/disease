# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:41:00 2015

@author: jpoles1
"""
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import numpy as np
import SocketServer
import json

themeColors = {"alive": "green", "infected": "orange", "dead": "red", "recovered": "blue"}
class Server(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
class Handler(SocketServer.StreamRequestHandler):
    def __init__(self, world):
        self.worldgraph = world.worldgraph;
    def handle(self):
        self.request.sendall(json.dumps(json_graph.node_link_data(self.worldgraph)))  # your JSON
class World:
    def __init__(self, initPopulation, serverPort):
        self.popsize = initPopulation;
        self.population = []
        self.diseaseList = {};
        self.age = 0;
        self.serverPort = serverPort
        for indv in range(initPopulation):
            self.population.append(Person(self));
        self.worldgraph = nx.watts_strogatz_graph(initPopulation, 4,  .3);
        mappin = {num: per for (num, per) in enumerate(self.population)}
        nx.relabel_nodes(self.worldgraph, mappin)
        nx.set_node_attributes(self.worldgraph, 'color', "green")
        server = Server(('127.0.0.1', self.serverPort), Handler(self))
        server.serve_forever()
    def death(self, person):
        self.popsize-=1;
        self.population.remove(person);
        self.worldgraph.remove_node(person);
    def addDisease(self, disease):
        pass
    def addPerson(self, person):
        self.population.append(person)
        self.popsize+=1;
        self.worldgraph
    def changeNodeColor(self, person, color):
        self.worldgraph.node[person]["fillcolor"] = color;
    def draw(self):
        return 0;        
        self.nodeLayout = nx.spring_layout(self.worldgraph)
        x.draw(self.worldgraph, layout=self.nodeLayout)
    def tick(self):
        self.age+=1;
        self.draw();
        interactions = random.sample(self.worldgraph.edges(), self.popsize/4)
class Town:
    pass
class Person:
    idct = 1;
    def __init__(self, world):
        #When infected, first check if disease is already in diseases, if not, check resistances
        self.diseases = [] #each entry is a disease ID
        self.id = Person.idct;
        Person.idct+=1;
        self.resistances = [] #each entry like {id: 1, resist: .05}
        self.world = world;
        self.color = themeColors["alive"]
    def infect(self, disease):
        self.diseases.append(disease);
        self.color = themeColors["infected"]
    def recover(self, disease, resist):
        try:
            self.diseases.remove(disease)
            self.color = themeColors["recovered"]
        except:
            pass
        self.resistances.append({"id": disease.id, "resist": resist})
    def checkDisease(a, b):
        newInfections = []
        for disease in a.diseases:
            if not any(dis for disease in b.diseases if dis['id'] == disease.id):
                try:
                    resistance = next(res for res in b.resistances if res['id'] == disease.id)
                    test = random.uniform(0, 1)
                    if(test>resistance["resist"]):
                        b.infect(disease);
                        newInfections.append(disease.id)
                except:
                    b.infect(disease);
                    newInfections.append(disease.id)
        return newInfections
    def interact(self, otherActor):
        print(Person.checkDisease(self, otherActor))
        print(Person.checkDisease(otherActor, self))
    def die(self):
        self.world.population.remove(self)
class Disease:
    idct = 1;
    diseaseList = []
    def __init__(self, world, virulence):
        self.id = Disease.idct;
        self.virulence = virulence;
        self.infected = 0;
        self.dead = 0;
        self.world = world;
        Disease.idct+=1;
        Disease.diseaseList.append(self);
    def mutateVirulence(self):
        virulenceJitter = .05;
        self.virulence = self.virulence + random.uniform(-virulenceJitter, virulenceJitter)
def testPeople():
    ali = Person()
    jordan = Person();
    cold = Disease(.8);
    ali.infect(cold)
    jordan.interact(ali)
def main():
    earth = World(100, 9090)
    runTime = 100;
    for i in range(runTime):
        earth.tick()
main()