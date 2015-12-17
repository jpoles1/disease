import random
import pandas as pd
class host:
    def __init__(self, populationSize):
        self.S = populationSize
        self.diseases = [];
        self.age = 0;
        self.history = pd.DataFrame()
        self.history["S"] = self.S
        self.step(5)
    def infect(self, name, disease, initInfected):
        self.diseases.append({"name": name, "pos": len(self.diseases)+1, "disease": disease, "I": initInfected})
        self.S-=initInfected
        self.step()
    def step(self, dt=1):
        for i in range(dt):
            self.history.loc[len(self.history)+1] = 0
            self.history.loc[len(self.history), "S"] = self.S
            if len(self.diseases) > 0:
                random.shuffle(self.diseases)
                s = self.S
                for dis in self.diseases:
                    self.S = s - dis["disease"].beta*s*dis["I"]+dis["disease"].gamma*dis["I"]
                    dis["I"] = dis["disease"].beta*dis["I"]*s - dis["disease"].gamma*dis["I"]
            self.age+=1;
            print "Step number %i, Age is %i" % (i, self.age)
class disease:
    def __init__(self, B, G):
        self.beta = B
        self.gamma = G
initialPop = 1e6
humans = host(initialPop)
killer = disease(.05, .01)
babby = disease(.05, .01)
humans.infect(1, killer, 15)
humans.infect(2, babby, 150)
humans.step(10)
humans.history