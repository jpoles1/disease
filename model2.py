# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:41:00 2015

@author: jpoles1
"""
from igraph import *
class World:
    def __init__(self, initPopulation):
        self.popsize = initPopulation;
        self.population = []
        for indv in range(initPopulation):
            self.population.append(Person());
        self.worldgraph = Graph.Watts_Strogatz(1, initPopulation, 5, 0.25);
        self.worldgraph.vs["classes"] = self.population
class Town:
    pass
class Person:
    idct = 1;
    def __init__(self):
        #When infected, first check if disease is already in diseases, if not, check resistances
        self.diseases = [] #each entry is a disease ID
        self.id = Person.idct;
        Person.idct+=1;
        self.resistances = [] #each entry like {id: 1, resist: .05}
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
    def die(self, world):
        world.popsize-=1;
        world.population.remove(self)
class Family:
    pass
class Disease:
    idct = 1;
    diseaseList = []
    def __init__(self):
        self.id = Disease.idct;
        Disease.idct+=1;
        Disease.diseaseList.append(self);
def testPeople():
    ali = Person()
    jordan = Person();
    cold = Disease();
    ali.infect(cold)
    jordan.interact(ali)
earth = World(100)
print("Average Vertex Degree: %f" % (mean(earth.worldgraph.degree())))
plot(earth.worldgraph, vertex_size=5, inline=1)