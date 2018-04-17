#!/usr/bin/env ruby

## M, T, AT -> MAP
## Author: Koki Hamada
## date: 2017-08-09

def read_table(f = $stdin)
  n = f.gets.chomp.to_i
  (0...n).map{f.gets.chomp}
end

def read_table_id(f = $stdin)
  n = f.gets.chomp.to_i
  (0...n).map{f.gets.chomp.split(/,/)[0]}
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


## constants
#months = ["2010/12", "2011/1", "2011/2", "2011/3", "2011/4", "2011/5", "2011/6", "2011/7", "2011/8", "2011/9", "2011/10", "2011/11", "2011/12"]
months = ["2010/12", "2011/1", "2011/2", "2011/3", "2011/4", "2011/5", "2011/6", "2011/7", "2011/8", "2011/9", "2011/10", "2011/11"]


## read M, T, AT
m = read_table()
t = read_table()
t0 = read_table()


## gen h ([original-id, month] -> id-in-T_0)
oids = m.map{|s| s.split(/,/)[0]}
i2oid = t.map{|s| s.split(/,/)[0]}

h = {}
t0.each_with_index do |s,i|
  next if s.strip == ''
  next if s.include?("DEL")
  oid = i2oid[i]
  x = s.split(/,/)
  id = x[0]
  raise "invalid date: '#{x[2]}'" unless /^(\d+\/\d+)\/\d+$/ =~ x[2]
  month = $1
  key = [oid, month]
  h[key] = id unless h[key]
  #raise "collision: [#{id}, #{month}] and [#{h[key]}, #{month}]" unless h[key] == id
end


## output
#$stdout.puts oids.size
oids.each do |oid|
  $stdout.puts oid + ',' + months.map{|m| h[[oid,m]] ? h[[oid,m]] : 'DEL'}.join(',')
end
