#!/usr/bin/env ruby
## create J file
## Author: Koki Hamada


def read_table(f = $stdin)
  n = f.gets.chomp.to_i
  (0...n).map{f.gets.chomp}
end

def write_table(t, f = $stdout, no_line_num = false)
  f.puts t.size unless no_line_num
  f.puts t
end

ARGV.each do |fname|
  File.open(fname) do |f|
    write_table(f.map{|x|x.chomp})
  end
end
