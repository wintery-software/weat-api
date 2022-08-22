require 'rails_helper'

RSpec.describe Restaurant, type: :model do
  describe '.sample' do
    it 'returns either one from whatever created' do
      restaurants = Array.new(3) do |index|
        Restaurant.create(name: "Restaurant #{index}")
      end

      restaurant = Restaurant.sample

      expect(restaurant).to be_instance_of(Restaurant)
      expect(restaurants).to include(restaurant)
    end

    it 'returns nil when there are no restaurants' do
      restaurant = Restaurant.sample

      expect(restaurant).to be_nil
    end
  end
end
