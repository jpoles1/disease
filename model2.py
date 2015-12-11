# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:41:00 2015

@author: jpoles1
"""
import networkx as nx
import random
from forceatlas import forceatlas2_layout
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

themeColors = {"alive": "green", "infected": "orange", "dead": "red", "recovered": "blue"}
class World:
    def __init__(self, initPopulation):
        self.popsize = initPopulation;
        self.population = []
        self.diseaseList = [];
        self.age = 0;
        for indv in range(initPopulation):
            self.population.append(Person(self));
        self.worldgraph = nx.watts_strogatz_graph(initPopulation, 4,  .3);
        mappin = {num: per for (num, per) in enumerate(self.population)}
        nx.relabel_nodes(self.worldgraph, mappin, copy=False)
        #self.nodeLayout = nx.spring_layout(self.worldgraph, k=.01)
        self.nodeLayout = forceatlas2_layout(self.worldgraph, iterations=100)
        nx.set_node_attributes(self.worldgraph, 'color', "green")
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
    def draw(self):
        nodeColors = [x.color for x in nx.nodes_iter(self.worldgraph)]
        plt.figure(figsize=(10,8))
        plt.title("Network at Age "+str(self.age))
        nx.draw(self.worldgraph, pos=self.nodeLayout, node_color=nodeColors, node_size=30, hold=1)
        plt.savefig("graphseries/graph"+str(self.age).zfill(4)+".png")
        plt.close()
    def tick(self):
        self.age+=1;
        if(self.age%4 == 0):
            self.draw();
        interactions = random.sample(self.worldgraph.edges(), self.popsize/6)
        for edge in interactions:
            edge[0].interact(edge[1])
        for person in self.population:
            pass
        for disease in self.diseaseList:
            print(disease.infected)
            disease.history[self.age] = disease.infected;
    def summary(self):
        history = {disease.id : disease.history for disease in self.diseaseList}
        return pd.DataFrame(history);
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
        self.alive = 1;
        self.color = themeColors["alive"]
    def infect(self, disease):
        self.diseases.append(disease);
        disease.infected+=1;
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
            if not any(dis for dis in b.diseases if dis.id == disease.id):
                try:
                    resistance = next(res for res in b.resistances if res['id'] == disease.id)
                    test = random.uniform(0, 1)
                    if(test>resistance["resist"]):
                        b.infect(disease);
                        newInfections.append(disease.id)
                    else:
                        print("individual resisted infection!")
                except:
                    b.infect(disease);
                    newInfections.append(disease.id)
        return newInfections
    def interact(self, otherActor):
        if(self.alive==1 and otherActor.alive==1):
            a = Person.checkDisease(self, otherActor);
            if(len(a)>0):
                print("Infections from A to B:", a)
            b = Person.checkDisease(otherActor, self);
            if(len(b)>0):
                print("Infections from B to A:", b)
    def die(self):
        self.alive = 0;
        self.color = themeColors["dead"]
class Disease:
    idct = 1;
    def __init__(self, world, virulence):
        self.id = Disease.idct;
        self.virulence = virulence;
        self.infected = 0;
        self.dead = 0;
        self.world = world;
        self.history = {};
        Disease.idct+=1;
        world.diseaseList.append(self);
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
    os.system("rm graphseries/*.png")
    earth = World(1000)
    runTime = 50;
    earth.tick()
    cold = Disease(earth, .8);
    earth.population[0].infect(cold)
    earth.population[50].recover(cold, .95)
    for i in range(runTime):
        earth.tick()
    print("Converting to GIF")
    os.system("convert -delay 50 -loop 0 graphseries/*.png graphseries/network.gif")
    print("Conversion complete")
    os.system('xdg-open graphseries/network.gif')
    return(earth.summary())
history = main()
plt.plot(history)