#!/usr/bin/Rscript --slave --vanilla
# usage: Rscript --slave --vanilla ran-psesup.R trans.csv [seed [min [map.csv]]] > an-trans.csv

pseudonym = function(m, t, seed = 628, minval=0){
  n = nrow(m)
  set.seed(seed)
  pid = unique(as.integer(runif(n * 1.1, min=minval, max=(minval + n*10) )))[1:n]
  lev = m[,1] # assumed as unique
  idm = factor(m[,1], levels = lev, labels = pid)
  idt = factor(t[,1], levels = lev, labels = pid)
  #m[,1] = idm
  names(pid) = m[,1]
  t[,1] = as.numeric(as.character(idt))
  return(list(f = pid,t = t))
}

outlier <- function(x, th = 4){
  return(x < (mean(x) - th * sd(x)) | x > (mean(x) + th * sd(x)) )
}

outliersup = function(t, th = 4){
  drop  <- outlier(t$V6, th)
#  t[,1] <- factor(t[,1])
  t[drop,1] = "DEL"
  return(t)
}

test = function(){
  m400 = read.csv("Master-Customer400.csv", header = F)
  t = read.csv("T-201012.csv", header = F)
  #cid = m[,1]
  #names(pid) = cid
}
m = read.csv("M.csv", header = F)

argv = commandArgs(T)
t = read.csv(argv[1], header = F)
seed = ifelse(length(argv) >1, as.integer(argv[2]), 628)
minval  = ifelse(length(argv) >2, as.integer(argv[3]), 100)

a = pseudonym(m, t, seed, minval)
ts = outliersup(a$t, th = 4)

#write.csv(a$t, row.names=F)
write.table(ts, row.names = F, quote = F, col.names = F, sep = ',')

if(length(argv) >3){
  write.table(a$f, file = argv[4], row.names = T, quote = F, col.names = F, sep = ',')
}else{
  write.table(a$f, row.names = T, quote = F, col.names = F, sep = ',')
}  

