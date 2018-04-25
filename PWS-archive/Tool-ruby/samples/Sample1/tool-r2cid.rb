#!/usr/bin/env ruby

## J(M, R) -> J(cid(R))

def read_table(f = $stdin)
  line = f.gets
  if line != nil then
    n = line.chomp.to_i
    (0...n).map{f.gets.chomp}
  end
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
  r = read_table(f)
  if r != nil then
    r.map{|x| x.to_i - 1}
  end
end

def write_p(p, f = $stdout, no_line_num = false)
  write_table(p.map{|x| x + 1}, f, no_line_num)
end

## read (M, R)
m = read_table()
r = read_p()


## write (J(m,cid))
write_table(m)

if r != nil then
  cid_r = r.map{|i| m[i].split(/,/)[0]}
  write_table(cid_r)
end



