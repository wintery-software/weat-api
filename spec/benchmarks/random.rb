require 'benchmark'

n = 100

Benchmark.bmbm do |x|
  x.report('RANDOM()') do
    n.times do
      Restaurant.order('RANDOM()').first
    end
  end
  x.report('pluck') do
    n.times do
      Restaurant.find(Restaurant.pluck(:id).sample)
    end
  end
end
