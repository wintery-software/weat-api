import pytest

from app.schemas.places import Location


def test_location_valid_coordinates():
    location = Location(latitude=37.7749, longitude=-122.4194)
    assert location.latitude == 37.7749
    assert location.longitude == -122.4194


def test_location_invalid_latitude():
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90 degrees"):
        Location(latitude=100.0, longitude=-122.4194)


def test_location_invalid_longitude():
    with pytest.raises(
        ValueError, match="Longitude must be between -180 and 180 degrees"
    ):
        Location(latitude=37.7749, longitude=200.0)
