class ApplicationController < ActionController::API
  def lucky
    picked = Restaurant.order('RANDOM()').first

    render :json => picked.name
  end
end
