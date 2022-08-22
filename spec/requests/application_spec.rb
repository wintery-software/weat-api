require 'rails_helper'

RSpec.describe 'Applications', type: :request do
  describe 'GET /lucky' do
    it 'gets a random restaurant on success' do
      Restaurant.create(name: '不二家酸菜鱼')
      get '/lucky'

      expect(response.content_type).to eq('application/json; charset=utf-8')
      expect(response).to have_http_status(:ok)

      response_body = JSON.parse(response.body)
      expect(response_body['name']).to eq('不二家酸菜鱼')
    end

    it 'gets nil on not found' do
      get '/lucky'

      expect(response.content_type).to eq('application/json; charset=utf-8')
      expect(response).to have_http_status(:not_found)

      response_body = JSON.parse(response.body)
      expect(response_body).to be_nil
    end
  end
end
