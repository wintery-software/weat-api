import json
from app import create_app, db
from app.models.restaurant import Restaurant
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item_category import RestaurantItemCategory


app = create_app()
root_path = "/Users/0x00-/Developer/acai/weat-api"


def seed():
    # Seed restaurant categories
    restaurant_categories_json_path = (
        f"{root_path}/data/dump/restaurant_categories.json"
    )
    with open(restaurant_categories_json_path) as f:
        restaurant_categories = json.load(f)
        for data in restaurant_categories:
            obj = RestaurantCategory.create(id=data["id"], name=data["name"])
            if data["name_zh"]:
                obj.add_translation("zh-CN", name=data["name_zh"])

    # Seed restaurants
    restaurants_json_path = f"{root_path}/data/dump/restaurants.json"
    with open(restaurants_json_path) as f:
        restaurants = json.load(f)
        for data in restaurants:
            obj = Restaurant.create(
                id=data["id"],
                name=data["name"],
                address=data["address"],
                google_place_id=data["place_id"],
                price=data["price"],
                rating=data["rating"],
                images=data["images"],
            )
            if data["name_zh"]:
                obj.add_translation("zh-CN", name=data["name_zh"])

    # Seed restaurant to category relationships
    restaurant_to_category_json_path = (
        f"{root_path}/data/dump/restaurant_to_category.json"
    )
    with open(restaurant_to_category_json_path) as f:
        restaurant_to_category = json.load(f)
        for data in restaurant_to_category:
            restaurant = Restaurant.get(id=data["restaurant_id"])
            category = RestaurantCategory.get(id=data["category_id"])

            if restaurant is None:
                raise ValueError(f"Restaurant not found (id={data['restaurant_id']})")
            if category is None:
                raise ValueError(f"Category not found (id={data['category_id']})")
            restaurant.add_category(category)

    # Seed restaurant item categories
    restaurant_item_categories_json_path = (
        f"{root_path}/data/dump/restaurant_item_categories.json"
    )
    with open(restaurant_item_categories_json_path) as f:
        restaurant_item_categories = json.load(f)
        for data in restaurant_item_categories:
            obj = RestaurantItemCategory.create(
                id=data["id"], name=data["name"], restaurant_id=data["restaurant_id"]
            )
            if data["name_zh"]:
                obj.add_translation("zh-CN", name=data["name_zh"])

    # Seed restaurant items
    restaurant_items_json_path = f"{root_path}/data/dump/restaurant_items.json"
    with open(restaurant_items_json_path) as f:
        restaurant_items = json.load(f)
        for data in restaurant_items:
            restaurant = Restaurant.get(id=data["restaurant_id"])
            if restaurant is None:
                raise ValueError(f"Restaurant not found (id={data['restaurant_id']})")

            obj = restaurant.add_item(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                price=data["price"],
                image=data["image"],
                category_id=data["category_id"],
            )
            if data["name_zh"]:
                obj.add_translation("zh-CN", name=data["name_zh"])


if __name__ == "__main__":
    with app.app.app_context():
        db.drop_all()
        db.create_all()

        seed()
