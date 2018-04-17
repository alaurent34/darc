#!/usr/bin/Rscript --slave --vanilla

bot = function(t){
  s.1.a = c(0.08,0.14,0.16,0.18,0.25,0.3,0.5,0.62,1.55,2.75,3,3.49,
            5.55,7.05,7.9,10.39,10.65,11.15,15.95,16.65,18,18.95,
            21.95,24.95,25,34.95,35.95,41.75,42.95,65,85,145,150
  )
  t.s1 = t$V6 %in% s.1.a
  return(t.s1)
}

argv = commandArgs(T)
t = read.csv(argv[1], header = F)

t.s1 = bot(t)
t[t.s1,1] = 'DEL'

#write.csv(a$t, row.names=F)
write.table(t, row.names = F, quote = F, col.names = F, sep = ',')
