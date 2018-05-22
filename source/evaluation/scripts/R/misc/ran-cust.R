#!/usr/bin/Rscript --slave --vanilla

drop.cust = function(t){
  t400.top.v = c('12748')
  t400.bot.v = c('12346','12603','12791','12814')
  t400.tb = c(t400.top.v, t400.bot.v)
  t.s = t$V1 %in% t400.tb
  return(t.s)
}

argv = commandArgs(T)
t = read.csv(argv[1], header = F)

t.s1 = drop.cust(t)
t[t.s1,1] = 'DEL'

#write.csv(a$t, row.names=F)
write.table(t, row.names = F, quote = F, col.names = F, sep = ',')
