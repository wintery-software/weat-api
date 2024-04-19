import pytest
from app.models.restaurant import Restaurant


valid_business_hours = [
    [],
    [
        {
            "start": "12:00",
            "end": "22:00"
        }
    ],
    [
        {
            "start": "12:00",
            "end": "22:00"
        }
    ],
    [
        {
            "start": "12:00",
            "end": "22:00"
        }
    ],
    [
        {
            "start": "12:00",
            "end": "22:00"
        }
    ],
    [
        {
            "start": "12:00",
            "end": "22:00"
        }
    ],
    [
        {
            "start": "12:00",
            "end": "14:00"
        },
        {
            "start": "17:00",
            "end": "22:00"
        }
    ]
]


def test_no_business_hours():
    obj = Restaurant.create(name="Test Restaurant")

    assert obj.id is not None
    assert obj.business_hours == None


def test_business_hours():
    obj = Restaurant.create(
        name="Test Restaurant",
        business_hours=valid_business_hours
    )

    assert obj.business_hours == valid_business_hours


def test_business_hours_invalid_number_of_days():
    with pytest.raises(ValueError):
        Restaurant.create(
            name="Test Restaurant",
            business_hours=[[{"start": "12:00", "end": "22:00"}]]
        )

def test_business_hours_invalid_time_range_missing_keys():
    with pytest.raises(ValueError):
        Restaurant.create(
            name="Test Restaurant",
            business_hours=[[{}],[],[],[],[],[],[]]
        )

def test_business_hours_invalid_time_range_end_before_start():
    with pytest.raises(ValueError):
        Restaurant.create(
            name="Test Restaurant",
            business_hours=[[{"start": "22:00", "end": "12:00"}],[],[],[],[],[],[]]
        )