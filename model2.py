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
from ggplot import *

themeColors = {"alive": "blue", "infected": "orange", "dead": "red", "recovered": "green"}
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
        plt.figure(figsize=(8,6))
        plt.title("Network at Age "+str(self.age))
        nx.draw(self.worldgraph, pos=self.nodeLayout, node_color=nodeColors, node_size=30, hold=1)
        plt.savefig("graphseries/graph"+str(self.age).zfill(4)+".png", dpi=250)
        plt.close()
    def tick(self):
        self.age+=1;
        if(self.age%4 == 0):
            print("Drawing network; Age is "+str(self.age))
            self.draw();
        interactions = random.sample(self.worldgraph.edges(), self.popsize/6)
        for edge in interactions:
            edge[0].interact(edge[1])
        for person in self.population:
            person.tick();
        for disease in self.diseaseList:
            disease.tick(self.age)
    def runSim(self, nsteps = 16):
        for i in range(nsteps):
            self.tick();
    def summary(self):
        histories = {}
        for disease in self.diseaseList:
            histories[disease.name] = disease.summary();
        return histories;
class Infection:
    def __init__(self, host, disease, timeToDeath, recoveryRate):
        self.host = host;
        self.disease = disease;
        self.timeToDeath = timeToDeath;
        self.recoveryRate = recoveryRate;
        self.id = disease.id;
        self.recovered = 0;
    def tick(self):
        self.timeToDeath-=1;
        if self.timeToDeath<1 and self.recovered!=1:
            self.host.die(self.disease)
        elif self.recovered!=1:
            test = random.uniform(0, 1)
            if(test>self.recoveryRate):
                self.host.recover(self, .9)
                self.recovered = 1;
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
        self.recoveryRate = random.uniform(.9, .99)
    def infect(self, disease):
        baseDeathTime = 32;
        self.diseases.append(Infection(self, disease, baseDeathTime*disease.pathogenicity, self.recoveryRate));
        disease.infected+=1;
        disease.susceptible-=1;
        self.color = themeColors["infected"]
    def recover(self, infection, resist):
        try:
            self.diseases.remove(infection)
        except:
            print("Infection not on list. Is this vaccination?");
        infection.disease.infected-=1;
        infection.disease.recovered+=1;
        self.color = themeColors["recovered"]
        self.resistances.append({"id": infection.disease.id, "resist": resist})
    def checkDisease(a, b):
        newInfections = []
        for disease in a.diseases:
            if not any(dis for dis in b.diseases if dis.id == disease.id):
                try:
                    resistance = next(res for res in b.resistances if res['id'] == disease.id)
                    test = random.uniform(0, 1)
                    if(test>resistance["resist"]):
                        b.infect(disease.disease);
                        newInfections.append(disease.id)
                    #else:
                        #print("individual resisted infection!")
                except:
                    b.infect(disease.disease);
                    newInfections.append(disease.id)
        return newInfections
    def interact(self, otherActor):
        if(self.alive==1 and otherActor.alive==1):
            a = Person.checkDisease(self, otherActor);
            b = Person.checkDisease(otherActor, self);
            '''if(len(a)>0):
                print("Infections from A to B:", a)
            if(len(b)>0):
                print("Infections from B to A:", b)'''
    def die(self, disease):
        if(self.alive==1):
            self.alive = 0;
            disease.infected-=1;
            disease.dead+=1;
            self.color = themeColors["dead"]
    def tick(self):
        if(self.alive==1):
            for infection in self.diseases:
                infection.tick()
class Disease:
    idct = 1;
    def __init__(self, name, world, virulence, pathogenicity):
        self.name = name;
        self.id = Disease.idct;
        self.virulence = virulence; #Determines how likely the pathogen is to spread from one host to the next
        self.pathogenicity = pathogenicity; #Determines how much disease the pathogen creates in the host (aka number of days w/o recovery until death)
        self.susceptible = world.popsize;
        self.infected = 0;
        self.recovered = 0;
        self.dead = 0;
        self.world = world;
        self.historyS = {};
        self.historyI = {};
        self.historyR = {}
        self.historyD = {}
        Disease.idct+=1;
        world.diseaseList.append(self);
    def mutateVirulence(self, virulenceJitter = .05):
        self.virulence = self.virulence + random.uniform(-virulenceJitter, virulenceJitter)
    def mutatePathogenicity(self, pathoJitter = .1):
        self.pathogenicity = self.pathogenicity + random.uniform(-pathoJitter, pathoJitter)
    def tick(self, age):
        self.historyS[age] = self.susceptible;
        self.historyI[age] = self.infected;
        self.historyR[age] = self.recovered;
        self.historyD[age] = self.dead;
    def summary(self):
        historyFrame = pd.DataFrame({"1-S": self.historyS, "2-I": self.historyI, "3-R": self.historyR, "4-D": self.historyD});
        historyFrame["time"] = historyFrame.index
        return historyFrame;
def main():
    os.system("rm graphseries/*.png")
    earth = World(1000)
    earth.tick()
    cold = Disease("Common Cold", earth, .7, 1);
    earth.population[0].infect(cold)
    earth.runSim(150)
    print("Converting to GIF")
    os.system("convert -delay 50 -loop 0 graphseries/*.png graphseries/network.gif")
    print("Conversion complete")
    os.system('xdg-open graphseries/network.gif')
    return(earth)
earth = main()
history = earth.summary() 
for name, x in history.iteritems():
    y = pd.melt(x, id_vars="time")
    z = ggplot(y, aes(x="time", y="value", color="variable"))+geom_line()+xlab("Time Step")+ylab("# Hiosts")+ylim(0, earth.popsize)+ggtitle("SIRD Dynamics - Agent Based Model\n"+name)
    ggsave(z, "graphs/"+name+".png")    
    print z