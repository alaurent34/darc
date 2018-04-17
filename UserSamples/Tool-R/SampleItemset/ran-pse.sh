
Rscript --slave --vanilla ran-pse.R Trans400.csv 0 > t0

cat Trans400-2010* Trans400-2011-[1-6].csv > t1a
cat Trans400-2011-[7-9].csv Trans400-2011-1?.csv > t1b

Rscript --slave --vanilla ran-pse.R t1a 1 >  t1
Rscript --slave --vanilla ran-pse.R t1b 2 >> t1


Rscript --slave --vanilla ran-pse.R  Trans400-2010-12.csv 30 > t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-1.csv  31 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-2.csv  32 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-3.csv  33 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-4.csv  34 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-5.csv  35 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-6.csv  36 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-7.csv  37 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-8.csv  38 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-9.csv  39 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-10.csv  310 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-11.csv  311 >> t3
Rscript --slave --vanilla ran-pse.R  Trans400-2011-12.csv  312 >> t3
