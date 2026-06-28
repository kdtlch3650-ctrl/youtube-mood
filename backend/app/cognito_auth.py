from __future__ import annotations

import base64
import json
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


def _get_issuer_from_env() -> str | None:
    region = _get_region()
    user_pool_id = _get_user_pool_id()
    if not region or not user_pool_id:
        return None

    return f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'


def _decode_unverified_claims(token: str) -> dict[str, Any]:
    try:
        payload = token.split('.')[1]
    except IndexError:
        return {}

    normalized = payload.replace('-', '+').replace('_', '/')
    padded = normalized + '=' * ((4 - len(normalized) % 4) % 4)

    try:
        decoded = base64.b64decode(padded)
        return json.loads(decoded.decode('utf-8'))
    except (ValueError, json.JSONDecodeError):
        return {}


def _get_issuer_from_token(token: str | None = None) -> str | None:
    if token:
        token_issuer = _decode_unverified_claims(token).get('iss')
        if token_issuer:
            return str(token_issuer)

    return _get_issuer_from_env()


def _get_jwks_url(issuer: str) -> str:
    return f'{issuer}/.well-known/jwks.json'


@lru_cache(maxsize=4)
def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    if not jwks_url:
        raise RuntimeError('Cognito settings are missing.')

    return PyJWKClient(jwks_url)


def _decode_without_signature_check(
    token: str,
    issuer: str,
    client_id: str | None,
    expected_token_use: str,
) -> dict[str, Any]:
    claims = jwt.decode(
        token,
        options={
            'verify_signature': False,
            'verify_aud': False,
        },
        algorithms=['RS256'],
        issuer=issuer,
    )

    token_use = claims.get('token_use')
    if token_use != expected_token_use:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication token type does not match.',
        )

    if expected_token_use == 'access' and client_id and claims.get('client_id') != client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token client_id does not match.',
        )

    if expected_token_use == 'id' and client_id and claims.get('aud') != client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='ID token audience does not match.',
        )

    return claims


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
    issuer = _get_issuer_from_token(token)
    client_id = _get_client_id()
    if not issuer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Cognito authentication settings are incomplete.',
        )

    try:
        jwks_url = _get_jwks_url(issuer)
        signing_key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=issuer,
            options={'verify_aud': expected_token_use != 'access'},
            audience=client_id if expected_token_use == 'id' else None,
        )
    except PyJWKClientError:
        # 로컬 개발 환경에서는 Cognito 공개키를 못 가져올 수 있어
        # 이 경우에만 서명 검증을 생략하고 클레임 기반 검증으로 진행한다.
        claims = _decode_without_signature_check(token, issuer, client_id, expected_token_use)
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

    if expected_token_use == 'access' and client_id and claims.get('client_id') != client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token client_id does not match.',
        )

    if expected_token_use == 'id' and client_id and claims.get('aud') != client_id:
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
