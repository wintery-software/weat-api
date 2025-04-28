import csv
import os
from dotenv import load_dotenv
import requests


load_dotenv()


API_BASE_URL = os.getenv("API_BASE_URL")
CREATE_PLACE_URL = f"{API_BASE_URL}/places/"
RESTAURANTS_FILE_PATH = "scripts/data/places_metadata - restaurants.csv"
DRINKS_FILE_PATH = "scripts/data/places_metadata - drinks.csv"


def add_places(file_path: str, type: str) -> None:
    file = open(file_path, encoding="utf-8")
    if not file:
        print(f"Error reading the file {file_path}")

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        payload = {
            "name": row.get("name"),
            "name_zh": row.get("name_translation") or None,
            "type": type,
            "address": row.get("address"),
            "latitude": (float(row["latitude"]) if row.get("latitude") else None),
            "longitude": (float(row["longitude"]) if row.get("longitude") else None),
            "google_maps_url": row.get("google_maps_url"),
            "google_maps_place_id": row.get("google_maps_place_id"),
        }

        print(f"Attempting to add: {payload.get('name')}")
        response = requests.post(CREATE_PLACE_URL, headers=headers, json=payload)
        print(response)
        response.raise_for_status()
        print(f"[{response.status_code}] Successfully added: {payload.get('name')}")


if __name__ == "__main__":
    # add_places(file_path=RESTAURANTS_FILE_PATH, type="food")
    add_places(file_path=DRINKS_FILE_PATH, type="food")
