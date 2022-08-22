class Restaurant < ApplicationRecord
  def self.sample
    Restaurant.order('RANDOM()').first
  end
end
