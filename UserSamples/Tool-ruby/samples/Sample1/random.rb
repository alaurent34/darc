#!/usr/bin/env ruby

## reidentify(random)
## J(M, S, T) -> J(f-hat,p-hat)
## Author: Koki Hamada
## date: 2017-08-31

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

## read M, T (or T'), S
m = read_table()
t = read_table()
t1 = read_table()

n = m.size
r = t1.map{rand(n)}

f = make_dummy_f_hat(m, t, t1)

## write f-hat, p-hat
write_table(f)
write_p(r)
