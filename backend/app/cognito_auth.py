from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, TypedDict

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError


class AuthenticatedUser(TypedDict):
    user_id: str
    user_email: str | None


def _get_region() -> str | None:
    return os.getenv('COGNITO_REGION') or os.getenv('AWS_REGION')


def _get_user_pool_id() -> str | None:
    return os.getenv('COGNITO_USER_POOL_ID')


def _get_client_id() -> str | None:
    return os.getenv('COGNITO_APP_CLIENT_ID')


def _get_issuer() -> str | None:
    region = _get_region()
    user_pool_id = _get_user_pool_id()
    if not region or not user_pool_id:
        return None

    return f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'


def _get_jwks_url() -> str | None:
    issuer = _get_issuer()
    if not issuer:
        return None

    return f'{issuer}/.well-known/jwks.json'


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    jwks_url = _get_jwks_url()
    if not jwks_url:
        raise RuntimeError('Cognito settings are missing.')

    return PyJWKClient(jwks_url)


def _normalize_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header must use the Bearer scheme.',
        )

    return token.strip()


def _decode_verified_token(token: str, expected_token_use: str) -> dict[str, Any]:
    issuer = _get_issuer()
    client_id = _get_client_id()
    if not issuer or not client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Cognito authentication settings are incomplete.',
        )

    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=issuer,
            options={'verify_aud': expected_token_use != 'access'},
            audience=client_id if expected_token_use == 'id' else None,
        )
    except PyJWKClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Failed to load Cognito public keys.',
        ) from exc
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication token has expired.',
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication token is invalid.',
        ) from exc

    token_use = claims.get('token_use')
    if token_use != expected_token_use:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication token type does not match.',
        )

    if expected_token_use == 'access' and claims.get('client_id') != client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token client_id does not match.',
        )

    if expected_token_use == 'id' and claims.get('aud') != client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='ID token audience does not match.',
        )

    return claims


def get_authenticated_user(
    authorization: str | None = Header(default=None),
    x_cognito_id_token: str | None = Header(default=None, alias='X-Cognito-Id-Token'),
) -> AuthenticatedUser | None:
    access_token = _normalize_bearer_token(authorization)
    if not access_token:
        return None

    access_claims = _decode_verified_token(access_token, 'access')
    user_email: str | None = None

    if x_cognito_id_token:
        id_claims = _decode_verified_token(x_cognito_id_token, 'id')
        user_email = id_claims.get('email') or id_claims.get('username')
    else:
        user_email = access_claims.get('username')

    user_id = access_claims.get('sub') or access_claims.get('username')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unable to identify the authenticated user.',
        )

    return {
        'user_id': str(user_id),
        'user_email': str(user_email) if user_email else None,
    }
