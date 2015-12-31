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
#Configuration
themeColors = {"alive": "blue", "infected": "orange", "dead": "red", "recovered": "green"}
drawgif = 1;
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
        self.nodeLayout = forceatlas2_layout(self.worldgraph, iterations=100, linlog=1)
        nx.set_node_attributes(self.worldgraph, 'color', themeColors["alive"])
    def draw(self):
        if(drawgif):
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
        interactions = random.sample(self.worldgraph.edges(), self.popsize/4)
        for edge in interactions:
            edge[0].interact(edge[1])
        for person in self.population:
            person.tick();
        for disease in self.diseaseList:
            disease.tick(self.age)
    def runSim(self, nsteps):
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
        if not self.recovered:
            self.timeToDeath-=1;
            if self.timeToDeath<1:
                self.host.die(self.disease)
            else:
                test = random.uniform(0, 1)
                if(test>self.recoveryRate):
                    self.host.recover(self)
                    self.recovered = 1;
class Person:
    idct = 1;
    def __init__(self, world):
        #When infected, first check if disease is already in diseases, if not, check resistances
        self.infections = {}
        self.id = Person.idct;
        Person.idct+=1;
        self.resistances = {}
        self.world = world;
        self.alive = 1;
        self.color = themeColors["alive"]
        self.recoveryRate = random.uniform(.9, .99)
        self.resistance = .9
        #self.resistanceCoeff = random.uniform(.5, 1)*(self.age-40)^2*(1/1600)
    def infect(self, disease, wasResistant):
        baseDeathTime = 32;
        self.infections[disease.id] = Infection(self, disease, baseDeathTime*disease.pathogenicity, self.recoveryRate);
        disease.infected+=1;
        if wasResistant:
            disease.resistant-=1;
        else:
            disease.susceptible-=1;
        self.color = themeColors["infected"]
    def recover(self, infection):
        try:
            self.infections[infection.disease.id] = 0
            infection.disease.infected-=1;
            infection.disease.resistant+=1;
        except:
            print("Infection not on list. Is this vaccination?");
        self.color = themeColors["recovered"]
        self.resistances[infection.disease.id] = self.resistance
    def checkDisease(a, b):
        newInfections = []
        for diseaseid, infection in a.infections.iteritems():
            if b.infections.get(diseaseid, 0)==0 and infection!=0:
                resistance = b.resistances.get(diseaseid, -1);
                if resistance!=-1:
                    test = random.uniform(0, 1)
                    if(test>resistance):
                        b.infect(infection.disease, 1);
                        newInfections.append(infection.disease.id)
                    #else:
                        #print("individual resisted infection!")
                else:
                    b.infect(infection.disease, 0);
                    newInfections.append(infection.disease.id)
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
            for diseaseid, infection in self.infections.iteritems():
                if(infection!=0):
                    infection.tick()
class Disease:
    idct = 1;
    def __init__(self, name, world, virulence, pathogenicity):
        self.name = name;
        self.id = Disease.idct;
        Disease.idct+=1;
        self.virulence = virulence; #Determines how likely the pathogen is to spread from one host to the next
        self.pathogenicity = pathogenicity; #Determines how much disease the pathogen creates in the host (aka number of days w/o recovery until death)
        self.susceptible = world.popsize;
        self.infected = 0;
        self.resistant = 0;
        self.dead = 0;
        self.world = world;
        self.historyS = {};
        self.historyI = {};
        self.historyR = {}
        self.historyD = {}
        world.diseaseList.append(self);
    #These two functions are not currently in use. They don't fit into the current model
    '''def mutateVirulence(self, virulenceJitter = .05):
        self.virulence = self.virulence + random.uniform(-virulenceJitter, virulenceJitter)
    def mutatePathogenicity(self, pathoJitter = .1):
        self.pathogenicity = self.pathogenicity + random.uniform(-pathoJitter, pathoJitter)'''
    def tick(self, age):
        self.historyS[age] = self.susceptible;
        self.historyI[age] = self.infected;
        self.historyR[age] = self.resistant;
        self.historyD[age] = self.dead;
    def summary(self):
        historyFrame = pd.DataFrame({"1-S": self.historyS, "2-I": self.historyI, "3-R": self.historyR, "4-D": self.historyD});
        historyFrame["time"] = historyFrame.index
        return historyFrame;
def main():
    os.system("rm graphseries/*.png")
    earth = World(1000)
    earth.tick()
    cold = Disease("Common Cold", earth, .95, 1);
    earth.population[0].infect(cold, 0)
    earth.population[1].infect(cold, 0)
    earth.runSim(150)
    if(drawgif):
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