#!/usr/bin/env ruby

## ramdomly delete some transactions
## date: 2017-09-06

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

## read M, T
m = read_table()
t = read_table()

# delete
del_rate = 0.1
t0 = t.map{|x| rand() < del_rate ? "DEL,,,,,," : x}

original_ids = m.map{|s| s.split(/,/)[0]}
n = original_ids.size
new_ids = (0...n).map{|i| sprintf("9%05d", i)}.shuffle
original2new = Hash[[original_ids, new_ids].transpose]
t0 = t0.map{|s|
  a = s.split(/,/)
  a[0] = original2new[a[0]] unless a[0] == 'DEL'
  raise unless a[0]
  a.join(',')
}

## write M, T, T0
write_table(m)
write_table(t)
write_table(t0)
