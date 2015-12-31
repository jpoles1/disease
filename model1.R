#SIRD Model of Disease Transmission
S=1000
I=15
R=0
D=0
beta=.0005
gamma=.05
mu=.02
#Create History Dataframe
history = data.frame(time=0, S=S,I=I,R=R,D=D);
#Create Time Step Function pmax used so values cannot drop below 0
stepDisease = function(time, Beta, Gamma, Mu){
  newS = pmax(S - (Beta*I*S), 0)
  newI = pmax(I + (Beta*I*S) - (Gamma*I) - (Mu*I), 0)
  newR = pmax(R + (Gamma*I), 0)
  newD = pmax(D + (Mu*I), 0)
  S <<- newS; I <<- newI; R <<- newR; D <<- newD;
  return(data.frame(time, S, I, R, D))
}
#Loop over step function
nreps = 100
for(i in 1:nreps){
  history = rbind(history, stepDisease(i, beta, gamma, mu))
}
#And finally plot
require(reshape2)
require(ggplot2)
plotdat = melt(history, id.vars = c("time"))
ggplot(data=plotdat)+
  aes(x=time, y=value, color=variable)+
  geom_line(size=2)+
  theme_set(theme_gray(base_size = 24))+
  xlab("Time Step")+ylab("# Indv.")+
  ggtitle(paste("SIRD Dynamics\nβ=",beta,"; γ=",gamma,"; μ=",mu,"\n", sep=""))+
  scale_color_manual(name="Disease State", 
    values=c("blue", "orange", "green", "red"))