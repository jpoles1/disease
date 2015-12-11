# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:41:00 2015

@author: jpoles1
"""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class World:
    def __init__(self, initPopulation):
        self.popsize = initPopulation;
        self.population = []
        self.diseaseList = {};
        for indv in range(initPopulation):
            self.population.append(Person(self));
        self.worldgraph = nx.watts_strogatz_graph(initPopulation, 4,  .3);
        mappin = {num: per for (num, per) in enumerate(self.population)}
        nx.relabel_nodes(self.worldgraph, mappin)
        nx.set_node_attributes(self.worldgraph, 'fillcolor', "green")
    def death(self, person):
        self.popsize-=1;
        self.population.remove(person);
        self.worldgraph.remove_node(person);
    def addDisease(self, disease):
    def addPerson(self, person):
        self.population.append(person)
        self.popsize+=1;
        self.worldgraph
    def changeNodeColor(self, person, color):
        self.worldgraph.node[person]["fillcolor"] = color;
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
    def infect(self, disease):
        self.diseases.append(disease)
    def recover(self, disease, resist):
        try:
            self.diseases.remove(disease)
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
def tick(world):
    for edge in world.
def main():
    earth = World(100)
    nx.draw_spring(earth.worldgraph)
    for i in range(runTime):
        tick(earth)
runtime = 100;
main()