#!/usr/bin/Rscript --slave --vanilla

pseudonym = function(m, t, seed = 628, min=0){
  n = nrow(m)
  set.seed(seed)
  pid = unique(as.integer(runif(n * 1.1, min=min, max=min + n * 10)))[1:n]
  lev = m[,1] # assumed as unique
  idm = factor(m[,1], levels = lev, labels = pid)
  idt = factor(t[,1], levels = lev, labels = pid)
  m[,1] = idm
  t[,1] = idt
  return(list(m = m,t = t))
}

m400 = read.csv("Master-Customer400.csv", header = F)
#m = read.csv("tiny-mst.csv", header = F)

argv = commandArgs(T)
t = read.csv(argv[1], header = F)
seed = ifelse(length(argv) >1, argv[2], 628)

a = pseudonym(m400, t, seed)

#write.csv(a$t, row.names=F)
write.table(a$t, row.names = F, quote = F, col.names = F, sep = ',')
