from uuid import UUID

from sqlalchemy import Float, cast, func, or_, select
from sqlalchemy.exc import IntegrityError

from app.constants import PLACE_SEARCH_SIMILARITY_THRESHOLD
from app.models.places import Place
from app.models.tags import Tag
from app.models.uow import DBUnitOfWork
from app.schemas.places import LocationBounds, PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.common import paginate, with_similarity_threshold
from app.services.errors import (
    ObjectNotFoundError,
    ValidationError,
)


class InvalidTagIdError(ValidationError):
    """Custom error for invalid tag IDs."""

    def __init__(self, tag_ids: list[UUID]) -> None:
        super().__init__(f"Invalid tag IDs: {tag_ids}")
        self.tag_ids = tag_ids


def _validate_tags(tags: list[Tag], tag_ids: list[UUID]) -> None:
    """Validate that the tags match the provided tag IDs.

    Args:
        tags (list[Tag]): List of tags to validate.
        tag_ids (list[UUID]): List of tag IDs to match against.

    Raises:
        InvalidTagIdError: If the tags do not match the provided tag IDs.

    """
    if len(set(tags)) != len(set(tag_ids)):
        raise InvalidTagIdError(tag_ids)


async def _get_place_by_id(db: DBUnitOfWork, place_id: UUID) -> Place:
    place = await db.get_by_id(Place, place_id)

    if place is None:
        raise ObjectNotFoundError(Place.__class__, place_id)

    return place


async def _get_tags_by_ids(db: DBUnitOfWork, tag_ids: list[UUID]) -> list[Tag]:
    stmt = select(Tag).where(Tag.id.in_(tag_ids))
    return await db.get_all(stmt)


async def _assign_tags_to_place(
    db: DBUnitOfWork,
    place: Place,
    tag_ids: list[UUID],
) -> None:
    tags = await _get_tags_by_ids(db, tag_ids)
    _validate_tags(tags, tag_ids)
    place.tags = tags


async def list_paginated_places(
    db: DBUnitOfWork,
    bounds: LocationBounds | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[PlaceResponse], int]:
    """List places within a specified bounding box.

    Args:
        db (DBUnitOfWork): The database unit of work.
        bounds (LocationBounds, optional): The bounding box for filtering places.
        page (int, optional): The page number for pagination. Defaults to 1.
        page_size (int, optional): The number of items per page. Defaults to 10.

    Returns:
        tuple[list[PlaceResponse], int]: A tuple containing a list of place responses
        and the total count of places.

    """
    if not bounds:
        bounds = LocationBounds(
            sw_lat=-90,
            sw_lng=-180,
            ne_lat=90,
            ne_lng=180,
        )

    stmt = select(Place).where(
        Place.location_geom.op("&&")(
            func.ST_MakeEnvelope(
                bounds.sw_lng,
                bounds.sw_lat,
                bounds.ne_lng,
                bounds.ne_lat,
                4326,
            ),
        ),
    )
    items, total = await paginate(db, stmt, page, page_size)

    items = [PlaceResponse.model_validate(item) if item else None for item in items]

    return items, total


async def search_paginated_places(
    db: DBUnitOfWork,
    q: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[PlaceResponse], int]:
    """Search for places based on a query string.

    Args:
        db (DBUnitOfWork): The database unit of work.
        q (str, optional): The search query string. Defaults to None.
        page (int, optional): The page number for pagination. Defaults to 1.
        page_size (int, optional): The number of items per page. Defaults to 10.

    Returns:
        tuple[list[PlaceResponse], int]: A tuple containing a list of place responses
        and the total count of places.

    """
    await with_similarity_threshold(db, PLACE_SEARCH_SIMILARITY_THRESHOLD)

    stmt = select(Place).join(Place.tags, isouter=True)
    if q:
        stmt = stmt.where(
            or_(
                Place.name.op("%")(q),
                Place.name_zh.op("%")(q),
                Place.address.op("%")(q),
            ),
        )
        stmt = stmt.order_by(
            cast(Place.name.op("<->")(q), Float)
            + cast(Place.name_zh.op("<->")(q), Float) * 1.5
            + cast(Place.address.op("<->")(q), Float) * 2,
        )
    items, total = await paginate(db, stmt, page, page_size)

    items = [PlaceResponse.model_validate(item) if item else None for item in items]

    return items, total


async def create_place(db: DBUnitOfWork, place_create: PlaceCreate) -> PlaceResponse:
    """Create a new place.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_create (PlaceCreate): The place creation data.

    Returns:
        PlaceResponse: The created place response.

    Raises:
        DuplicateGoogleMapsPlaceIdError: If the Google Maps Place ID already exists.
        ValidationError: If there is a validation error.

    """
    place = Place(**place_create.model_dump(exclude={"tag_ids"}))
    await _assign_tags_to_place(db, place, place_create.tag_ids)
    await db.add(place)

    try:
        await db.commit()
    except IntegrityError as e:
        if f"Key (google_maps_place_id)=({place.google_maps_place_id}) already exists" in str(e):
            raise DuplicateGoogleMapsPlaceIdError(place.google_maps_place_id) from e

        raise ValidationError from e

    await db.refresh(place)

    return PlaceResponse.model_validate(place)


async def get_place(db: DBUnitOfWork, place_id: UUID) -> PlaceResponse:
    """Get a place by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_id (UUID): The ID of the place to retrieve.

    Returns:
        PlaceResponse: The place response.

    """
    place = await _get_place_by_id(db, place_id)

    return PlaceResponse.model_validate(place)


async def update_place(
    db: DBUnitOfWork,
    place_id: UUID,
    place_update: PlaceUpdate,
) -> PlaceResponse:
    """Update a place by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_id (UUID): The ID of the place to update.
        place_update (PlaceUpdate): The updated place data.

    Returns:
        PlaceResponse: The updated place response.

    Raises:
        DuplicateGoogleMapsPlaceIdError: If the Google Maps Place ID already exists.
        ValidationError: If there is a validation error.

    """
    place = await _get_place_by_id(db, place_id)

    place.update(place_update)
    await _assign_tags_to_place(db, place, place_update.tag_ids)
    await db.add(place)

    try:
        await db.commit()
    except IntegrityError as e:
        if f"Key (google_maps_place_id)=({place.google_maps_place_id}) already exists" in str(e):
            raise DuplicateGoogleMapsPlaceIdError(place.google_maps_place_id) from e

        raise ValidationError from e

    await db.refresh(place)

    return PlaceResponse.model_validate(place)


async def delete_place(db: DBUnitOfWork, place_id: UUID) -> None:
    """Delete a place by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_id (UUID): The ID of the place to delete.

    """
    place = await _get_place_by_id(db, place_id)

    await db.delete(place)
    await db.commit()


class DuplicateGoogleMapsPlaceIdError(ValidationError):
    """Custom error for duplicate Google Maps Place ID."""

    def __init__(self, google_maps_place_id: UUID) -> None:
        super().__init__(f"Duplicate Google Maps Place ID: {google_maps_place_id}")
