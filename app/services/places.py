from uuid import UUID

from sqlalchemy import Float, cast, func, or_, select
from sqlalchemy.exc import IntegrityError

from app.constants import PLACE_SEARCH_SIMILARITY_THRESHOLD
from app.db.uow import DBUnitOfWork
from app.models.place import Place
from app.models.tag import Tag
from app.schemas.errors import InvalidSortColumnError
from app.schemas.options import FilterOptions, PaginationOptions, SortOptions
from app.schemas.places import LocationBounds, PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.common import paginate, sort, with_similarity_threshold
from app.services.errors import (
    ObjectNotFoundError,
    ValidationError,
)


async def _get_place_by_id(db: DBUnitOfWork, place_id: UUID) -> Place:
    """Get a place by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_id (UUID): The ID of the place to retrieve.

    Returns:
        Place: The place.

    Raises:
        ObjectNotFoundError: If the place is not found.

    """
    place = await db.get(Place, place_id)

    if not place:
        raise ObjectNotFoundError(Place.__name__, place_id)

    return place


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


async def list_places(
    db: DBUnitOfWork,
    bounds: LocationBounds | None = None,
    sort_options: SortOptions | None = None,
    filter_options: FilterOptions | None = None,
    pagination_options: PaginationOptions | None = None,
) -> tuple[list[PlaceResponse], int] | list[PlaceResponse]:
    """List places with optional bounds filtering.

    Args:
        db (DBUnitOfWork): The database unit of work.
        bounds (LocationBounds): The bounds for filtering places.
        sort_options (SortOptions, optional): The sort options. Defaults to None.
        filter_options (FilterOptions): The filter options.
        pagination_options (PaginationOptions): The pagination options.

    Returns:
        tuple[list[PlaceResponse], int]: A tuple containing a list of place responses
        and the total count of places.

    Raises:
        InvalidSortColumnError: If the sort column is invalid.

    """
    # Start with a base statement
    stmt = select(Place).join(Place.tags, isouter=True)

    # Add boundaries to the statement
    if bounds:
        await with_similarity_threshold(db, PLACE_SEARCH_SIMILARITY_THRESHOLD)
        stmt = stmt.where(
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

    # Add a filtering query to the statement
    if filter_options:
        q = filter_options.q
        stmt = stmt.where(
            or_(
                Place.name.op("%")(q),
                Place.name_zh.op("%")(q),
                Place.address.op("%")(q),
            ),
        )
        # Only apply text search ordering if no explicit sort is requested
        if not sort_options:
            stmt = stmt.order_by(
                cast(Place.name.op("<->")(q), Float)
                + cast(Place.name_zh.op("<->")(q), Float) * 1.5
                + cast(Place.address.op("<->")(q), Float) * 2,
            )

    # Add a sorting query to the statement
    if sort_options:
        if not hasattr(Place, sort_options.sort_by):
            raise InvalidSortColumnError(sort_options.sort_by)

        stmt = sort(stmt, Place, sort_options.sort_by, sort_options.order)

    # Add a pagination query to the statement
    if pagination_options:
        total = await db.get_count(stmt)
        stmt = paginate(stmt, pagination_options.page, pagination_options.page_size)

    # Execute the statement
    items = await db.get_all(stmt)
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
