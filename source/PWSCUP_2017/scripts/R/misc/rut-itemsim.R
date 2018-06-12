#!/usr/bin/Rscript --slave --vanilla

t400  = read.csv("Trans400.csv", header = F)

reduce.topk = function(t, k){
  t.topk.item = sort(table(t400$V5), decreasing = T)[1:k]
  t.topk.i = t$V5 %in% names(t.topk.item)
  return(t[t.topk.i,])
}

sim0 = function(t){
  t.r = reduce.topk(t, 100)
  t.r.sim = items.sim2(t.r)
  return(t.r.sim)
}

items.sim2 = function(t){
  t.51 = table(factor(t$V5), factor(t$V1))
  t.sim = matrix(NA, nrow = nrow(t.51), ncol=nrow(t.51),
                 dimnames = list(rownames(t.51), rownames(t.51)))
  for(i in 1:nrow(t.51)){
    for(j in 1:nrow(t.51)){
      t.sim[j,i] = getCosine(t.51[i,], t.51[j,])
    }
  }
  return(t.sim)
}

getCosine <- function(x,y) {
  this.cosine <- sum(x*y) / (sqrt(sum(x*x)) * sqrt(sum(y*y)))
  return(this.cosine)
}

sim.dist = function(tx, ty, d = 10){
  tx.sim = sim0(tx)[1:d, 1:d]
  ty.sim = sim0(ty)[1:d, 1:d]
  return(mean(abs(tx.sim - ty.sim)))  
}

argv = commandArgs(T)
t = read.csv(argv[1], header = F)

cat(sim.dist(t, t400), "\n")
