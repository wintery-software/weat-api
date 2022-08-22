class ApplicationController < ActionController::API
  def lucky
    restaurant = Restaurant.sample

    if restaurant
      render :json => {name: restaurant.name}
    else
      render :json => nil
    end
  end
end
