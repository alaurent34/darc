#!/usr/bin/env ruby

## evaluate re-identified result
## J(M, T, P, R) -> TCM
## author: khamada
## date: 2017-08-17

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


def p2ans(m, t, p)
  id2i = {}
  m.each_with_index{|s, i| id2i[s.split(/,/)[0]] = i}
  p.map{|i| id2i[t[i].split(/,/)[0]]}
end

## read M, T, P, R
m = read_table()
t = read_table()
p = read_p()
r = read_p()

## compute answer
ans = p2ans(m, t, p)

## compare R with ans
hit = [r, ans].transpose.map{|x,y| x == y ? 1 : 0}.inject(0){|c,i|c+i}
$stdout.puts hit.to_f / r.size
