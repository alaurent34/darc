#!/usr/bin/Rscript --slave --vanilla
# usage: Rscript --slave --vanilla ut-cmae.R Anonymized.csv  Trans.csv  f.csv

cmae = function(ts, t, f){
  t.c1  = factor(t$V1, levels = names(f))
  t.c6  = tapply(t$V6,  t.c1,  mean, na.rm = T)
  t.co  = tapply(t.c6, m500[,c(3,4)], mean, na.rm =T)
  ts.c1 = factor(ts$V1, levels = f, labels = names(f))
  ts.c6 = tapply(ts$V6, ts.c1, mean, na.rm = T)
  ts.co = tapply(ts.c6, m500[,c(3,4)], mean, na.rm = T)
  return(mean(abs(t.co -ts.co), na.rm = T))
}


test = function(){
  t500  = read.csv("T.csv", header = F)
  t = read.csv("T-201012.csv", header = F)
  a = pseudonym(m, t, seed, minval)
  ts = outliersup(a$t, th = 4)
  f0 = read.csv("F-201012.csv", header = F)
  f1 = f0[,2]
  names(f1) = f0[,1]
  cmae(ts, t, f)
}
m500 = read.csv("M.csv", header = F)

argv = commandArgs(T)
ts = read.csv(argv[1], header = F)
t  = read.csv(argv[2], header = F)
f0 = read.csv(argv[3], header = F)
f  = f0[,2]
names(f) = f0[,1]

c = cmae(ts, t, f)
cat(c, "\n")