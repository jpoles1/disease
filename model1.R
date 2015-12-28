#SIR Model of Disease Transmission
Sinit = 1000
Iinit = 10
Rinit = 0
S=Sinit
I=Iinit
R=Rinit
D=0
history = data.frame(time=0, S=S,I=I,R=R,D=D);
#history = data.frame()
stepDisease = function(time, Beta, Gamma, Theta){
  newS = pmax(S - (Beta*I*S), 0)
  newI = pmax(I + (Beta*I*S) - (Gamma*I) - (Theta*I), 0)
  newR = pmax(R + (Gamma*I), 0)
  newD = pmax(D + (Theta*I), 0)
  S <<- newS; I <<- newI; R <<- newR; D <<- newD;
  return(data.frame(time, S, I, R, D))
}
nreps = 100
for(i in 1:nreps){
  history = rbind(history, stepDisease(i, .0005, .05, .02))
}
require(reshape2)
require(ggplot2)
plotdat = melt(history, id.vars = c("time"))
ggplot(data=plotdat, aes(time, value))+geom_line(aes(color=variable))
