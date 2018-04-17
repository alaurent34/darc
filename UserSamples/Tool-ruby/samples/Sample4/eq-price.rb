#!/usr/bin/env ruby

## reidentify by exact matching
## Author: Koki Hamada
## J(M, S, T^\alpha) -> J(f-hat,p-hat)
## date: 2017-08-31

## usage:
## $ ruby re-eq.rb [list of column indices that are used to match transactions]
##
## example:
## (1) match by (date, item id, unit price, num) (default)
## $ ruby re-eq.rb 2 4 5 6
## or
## $ ruby re-eq.rb
## (2) match by (date, time)
## $ ruby re-eq.rb 2 3
## (3) match by id
## $ ruby re-eq.rb 0
## (4) match by all attributes but id
## $ ruby re-eq.rb 1 2 3 4 5 6
## (5) match by (month, item)
## $ ruby re-eq.rb 7 2
##
## note:
##   a[7] := 'yyyy/mm' extracted from a[2]

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


def make_dummy_f_hat(m, t, t1)
  m.map{|s| [s.split(/,/)[0]] + ['DEL'] * 12}.sort.map{|a| a.join(',')}
end

def make_key(a, target)
  target.map{|i| a[i]}
end

def date2month(d)
  raise "invalid date: #{d}" unless /^(\d+)\/(\d+)\/\d+$/ =~ d
  "#{$1.to_i}/#{$2.to_i}"
end

def split_transaction(s)
  a = s.split(/,/)
  ## a[7] = 'yyyy/mm'
  a << date2month(a[2])
end

## read M, T (or T^\alpha), T1
m = read_table()
t1 = read_table()
t = read_table()

## reidentify
target = ARGV.map{|x| x.to_i}
##target = [2,4,5,6] if target.empty?
target = [2,5] if target.empty?

m_id2i = {}
m.each_with_index{|s,i| m_id2i[s.split(/,/)[0]] = i}

t_key2id = {}
t.each do |s|
  next if /^DEL,/ =~ s
  a = split_transaction(s)
  key = make_key(a, target)
  id = a[0]
  t_key2id[key] = [] unless t_key2id[key]
  t_key2id[key] << id
end

n = m.size
r = t1.map{|s|
  key = make_key(split_transaction(s), target)
  candidate = t_key2id[key]
  if candidate
    m_id2i[candidate.sample]
  else
    rand(n)
  end
}

f = make_dummy_f_hat(m, t, t1)

## write f-hat, p-hat
write_table(f)
write_p(r)
