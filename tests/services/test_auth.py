from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jose import JOSEError
from pytest_mock import MockerFixture

from app.routes.depends import get_admin_user, get_current_user

MOCK_KID = "test-kid"
MOCK_PUBLIC_KEY = {"kty": "RSA", "kid": MOCK_KID, "use": "sig", "n": "abc123", "e": "AQAB"}
MOCK_JWKS = {"keys": [MOCK_PUBLIC_KEY]}
MOCK_TOKEN = "mock.jwt.token"  # noqa: S105
MOCK_PAYLOAD = {"sub": "123", "email": "test@example.com"}
MOCK_ADMIN_PAYLOAD = {
    "sub": "123",
    "email": "admin@example.com",
    "cognito:groups": ["admin"],
}


@pytest.mark.asyncio
async def test_get_current_user_success(mocker: MockerFixture) -> None:
    """Test the get_current_user function with a valid token."""
    # Mock the HTTP call to JWKS URL
    mock_response = mocker.Mock()
    mock_response.json.return_value = MOCK_JWKS
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    # Mock JWT processing
    mocker.patch("jose.jwt.get_unverified_header", return_value={"kid": MOCK_KID})
    mocker.patch("jose.utils.base64url_decode", return_value=b"decoded-bytes")
    mocker.patch("jose.jwk.construct", return_value="mock-public-key")
    mocker.patch("jose.jwt.decode", return_value=MOCK_PAYLOAD)

    result = await get_current_user(MOCK_TOKEN)
    assert result == MOCK_PAYLOAD


@pytest.mark.asyncio
async def test_get_current_user_kid_not_found(mocker: MockerFixture) -> None:
    """Test the get_current_user function when the kid is not found in JWKS."""
    # JWKS doesn't contain the needed key
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"keys": []}
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    mocker.patch("jose.jwt.get_unverified_header", return_value={"kid": "missing-kid"})

    with pytest.raises(HTTPException) as exc:
        await get_current_user(MOCK_TOKEN)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert "Invalid token header" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_decode_fails(mocker: MockerFixture) -> None:
    """Test the get_current_user function when decoding the token fails."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = MOCK_JWKS
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    mocker.patch("jose.jwt.get_unverified_header", return_value={"kid": MOCK_KID})
    mocker.patch("jose.utils.base64url_decode", return_value=b"decoded-bytes")
    mocker.patch("jose.jwk.construct", return_value="mock-public-key")
    mocker.patch("jose.jwt.decode", side_effect=JOSEError("bad token"))

    with pytest.raises(HTTPException) as exc:
        await get_current_user(MOCK_TOKEN)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert "Invalid token header" in exc.value.detail


@pytest.mark.asyncio
async def test_get_admin_user_success() -> None:
    """Test the get_admin_user function with a valid token."""
    result = await get_admin_user(MOCK_ADMIN_PAYLOAD)
    assert result == MOCK_ADMIN_PAYLOAD


@pytest.mark.asyncio
async def test_get_admin_user_not_admin() -> None:
    """Test the get_admin_user function when the user is not an admin."""
    with pytest.raises(HTTPException) as exc:
        await get_admin_user(MOCK_PAYLOAD)

    assert exc.value.status_code == HTTPStatus.FORBIDDEN
    assert "Not an admin user" in exc.value.detail
