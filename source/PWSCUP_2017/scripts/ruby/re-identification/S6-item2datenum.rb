#!/usr/bin/env ruby

## J(M, S, T) -> J(H)
##
## If all attributes in 'attr' are the same between an anonymized transaction i and an original transaction j,
## then the algorithm regards i as the anonymized transaction of j.
## The attributes are identified by the following indices:
## - 0: customer ID
## - 1: invoice number
## - 2: date
## - 3: time
## - 4: item ID
## - 5: unit price
## - 6: quantity
## - 7: first two characters of item ID
##
## (c) 2017 Koki Hamada

def read_table(f = $stdin)
  n = f.gets.chomp.to_i
  (0...n).map{f.gets.chomp}
end

def read_table_skip(f = $stdin)
  n = f.gets.chomp.to_i
  n.times{f.gets}
end

def write_table(t, f = $stdout, no_line_num = false)
  f.puts t.size unless no_line_num
  f.puts t
end

def read_p(f = $stdin)
  read_table(f).map{|x| x.to_i - 1}
end

def write_p(p, f = $stdout, no_line_num = false)
  write_table(p.map{|x| x + 1}, f, no_line_num)
end

MONTHS = ["2010/12", "2011/1", "2011/2", "2011/3", "2011/4", "2011/5", "2011/6", "2011/7", "2011/8", "2011/9", "2011/10", "2011/11"]
MONTHS2I = Hash[[MONTHS, (0...(MONTHS.size)).to_a].transpose]

def date2month_id(d)
  raise d unless /^(\d+\/\d+)\/\d+$/ =~ d
  m = $1
  raise m unless MONTHS2I[m]
  MONTHS2I[m]
end

def to_key(s, attr = [4, 2])
  a = s.split(/,/,-1)
  a << a[4].split(//)[0,2].join
  key = attr.map{|i| a[i]}.join(',')
end

def re_eq(oids, t, u, attr = [4, 2])
  key2pid = {}
  u.each do |s|
    a = s.split(/,/,-1)
    pid = a[0]
    #raise s if pid == 'DEL'
    key = to_key(s, attr)
    key2pid[key] = pid
  end
  oid2pids = {}
  oids.each{|oid| oid2pids[oid] = MONTHS.map{'DEL'}}
  t.each do |s|
    a = s.split(/,/,-1)
    oid, date = [a[0], a[2]]
    #raise s if oid == 'DEL'
    key = to_key(s, attr)
    next unless key2pid[key]
    i = date2month_id(date)
    oid2pids[oid][i] = key2pid[key]
  end
  oids.map{|oid| oid + "," + oid2pids[oid].join(',')}
end

## read M, S, T
m = read_table()
u = read_table()
t = read_table()

default_attr = [7, 2, 6]
attr = (ARGV.empty? ? default_attr : ARGV.map{|x| x.to_i})
oids = m.map{|s| s.split(/,/,-1)[0]}
h = re_eq(oids, t, u, attr)

## write H
write_table(h)
