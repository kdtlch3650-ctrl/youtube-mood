from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import os
import threading
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol
from urllib.parse import parse_qsl, quote, urlparse

import requests

from app.schemas import SearchRecord


class SearchRecordRepository(Protocol):
    def save(self, record: SearchRecord) -> SearchRecord:
        ...

    def list(self, user_id: str | None = None) -> list[SearchRecord]:
        ...


class InMemorySearchRecordRepository:
    def __init__(self, max_records: int = 100) -> None:
        self._records: list[SearchRecord] = []
        self._max_records = max_records

    def save(self, record: SearchRecord) -> SearchRecord:
        # 현재는 메모리에만 저장하고, 나중에 OpenSearch 저장소로 교체한다.
        self._records.append(record)
        del self._records[:-self._max_records]
        return record

    def list(self, user_id: str | None = None) -> list[SearchRecord]:
        records = list(reversed(self._records))
        if user_id is None:
            return records

        return [record for record in records if record.user_id == user_id]


@dataclass(slots=True)
class AwsCredentials:
    access_key_id: str
    secret_access_key: str
    session_token: str | None = None
    expiration: dt.datetime | None = None

    def is_expired(self, margin_seconds: int = 60) -> bool:
        if not self.expiration:
            return False

        return dt.datetime.now(dt.timezone.utc) >= self.expiration - dt.timedelta(seconds=margin_seconds)


class AwsCredentialsProvider:
    def __init__(self, region: str) -> None:
        self._region = region
        self._lock = threading.Lock()
        self._cached_credentials: AwsCredentials | None = None

    def get_credentials(self) -> AwsCredentials:
        with self._lock:
            if self._cached_credentials and not self._cached_credentials.is_expired():
                return self._cached_credentials

            credentials = self._load_from_env()
            if credentials is None:
                credentials = self._load_from_web_identity()

            self._cached_credentials = credentials
            return credentials

    def _load_from_env(self) -> AwsCredentials | None:
        access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if not access_key_id or not secret_access_key:
            return None

        return AwsCredentials(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=os.getenv('AWS_SESSION_TOKEN'),
        )

    def _load_from_web_identity(self) -> AwsCredentials:
        role_arn = os.getenv('AWS_ROLE_ARN')
        token_file = os.getenv('AWS_WEB_IDENTITY_TOKEN_FILE')
        if not role_arn or not token_file:
            raise RuntimeError('AWS credentials are not configured for OpenSearch access.')

        with open(token_file, encoding='utf-8') as token_stream:
            web_identity_token = token_stream.read().strip()

        sts_url = f'https://sts.{self._region}.amazonaws.com/'
        response = requests.post(
            sts_url,
            data={
                'Action': 'AssumeRoleWithWebIdentity',
                'Version': '2011-06-15',
                'RoleArn': role_arn,
                'RoleSessionName': 'youtube-mood-opensearch',
                'WebIdentityToken': web_identity_token,
            },
            timeout=15,
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        credentials_node = root.find('.//{*}Credentials')
        if credentials_node is None:
            raise RuntimeError('Failed to receive temporary AWS credentials.')

        access_key_id = (credentials_node.findtext('{*}AccessKeyId') or '').strip()
        secret_access_key = (credentials_node.findtext('{*}SecretAccessKey') or '').strip()
        session_token = (credentials_node.findtext('{*}SessionToken') or '').strip() or None
        expiration_text = (credentials_node.findtext('{*}Expiration') or '').strip()
        expiration = None
        if expiration_text:
            expiration = dt.datetime.fromisoformat(expiration_text.replace('Z', '+00:00'))

        if not access_key_id or not secret_access_key:
            raise RuntimeError('Temporary AWS credentials are incomplete.')

        return AwsCredentials(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            expiration=expiration,
        )


class AwsSigV4Signer:
    def __init__(self, region: str, service: str = 'es') -> None:
        self._region = region
        self._service = service

    def _sign(self, key: bytes, message: str) -> bytes:
        return hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, secret_key: str, date_stamp: str) -> bytes:
        key_date = self._sign(f'AWS4{secret_key}'.encode('utf-8'), date_stamp)
        key_region = self._sign(key_date, self._region)
        key_service = self._sign(key_region, self._service)
        return self._sign(key_service, 'aws4_request')

    def sign(
        self,
        method: str,
        url: str,
        credentials: AwsCredentials,
        body: bytes = b'',
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        parsed_url = urlparse(url)
        timestamp = dt.datetime.now(dt.timezone.utc)
        amz_date = timestamp.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = timestamp.strftime('%Y%m%d')

        canonical_uri = quote(parsed_url.path or '/', safe='/~')
        canonical_querystring = '&'.join(
            f'{quote(key, safe="-_.~")}={quote(value, safe="-_.~")}'
            for key, value in sorted(parse_qsl(parsed_url.query, keep_blank_values=True))
        )

        payload_hash = hashlib.sha256(body).hexdigest()
        signed_headers = {
            'host': parsed_url.netloc,
            'x-amz-date': amz_date,
        }
        if credentials.session_token:
            signed_headers['x-amz-security-token'] = credentials.session_token
        if headers:
            for key, value in headers.items():
                signed_headers[key.lower()] = value.strip()

        canonical_headers = ''.join(f'{key}:{signed_headers[key]}\n' for key in sorted(signed_headers))
        signed_header_names = ';'.join(sorted(signed_headers))

        canonical_request = '\n'.join(
            [
                method.upper(),
                canonical_uri,
                canonical_querystring,
                canonical_headers,
                signed_header_names,
                payload_hash,
            ]
        )

        credential_scope = f'{date_stamp}/{self._region}/{self._service}/aws4_request'
        string_to_sign = '\n'.join(
            [
                'AWS4-HMAC-SHA256',
                amz_date,
                credential_scope,
                hashlib.sha256(canonical_request.encode('utf-8')).hexdigest(),
            ]
        )

        signing_key = self._get_signature_key(credentials.secret_access_key, date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = (
            'AWS4-HMAC-SHA256 '
            f'Credential={credentials.access_key_id}/{credential_scope}, '
            f'SignedHeaders={signed_header_names}, '
            f'Signature={signature}'
        )

        signed_request_headers = {
            'Authorization': authorization_header,
            'x-amz-date': amz_date,
            'host': parsed_url.netloc,
        }
        if credentials.session_token:
            signed_request_headers['x-amz-security-token'] = credentials.session_token
        if headers:
            signed_request_headers.update(headers)

        return signed_request_headers


class OpenSearchSearchRecordRepository:
    def __init__(self) -> None:
        endpoint = os.getenv('OPENSEARCH_ENDPOINT', '').strip()
        if not endpoint:
            raise RuntimeError('OPENSEARCH_ENDPOINT is not configured.')

        if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
            endpoint = f'https://{endpoint}'

        self._endpoint = endpoint.rstrip('/')
        self._index_name = os.getenv('OPENSEARCH_INDEX', 'youtube-mood-search-records')
        self._region = os.getenv('OPENSEARCH_REGION') or os.getenv('AWS_REGION') or 'ap-northeast-2'
        self._service = os.getenv('OPENSEARCH_SERVICE', 'es')
        self._credentials_provider = AwsCredentialsProvider(self._region)
        self._signer = AwsSigV4Signer(self._region, self._service)
        self._index_ready = False
        self._index_lock = threading.Lock()

    def save(self, record: SearchRecord) -> SearchRecord:
        self._ensure_index()
        self._request(
            'PUT',
            f'/{self._index_name}/_doc/{record.id}?refresh=wait_for',
            json_body=record.model_dump(mode='json'),
        )
        return record

    def list(self, user_id: str | None = None) -> list[SearchRecord]:
        self._ensure_index()
        query: dict[str, object] = {
            'size': 100,
            'sort': [{'created_at': {'order': 'desc'}}],
        }
        if user_id:
            query['query'] = {'term': {'user_id': user_id}}
        else:
            query['query'] = {'match_all': {}}

        response = self._request('POST', f'/{self._index_name}/_search', json_body=query)
        payload = response.json()
        hits = payload.get('hits', {}).get('hits', [])
        return [SearchRecord(**hit.get('_source', {})) for hit in hits]

    def _ensure_index(self) -> None:
        if self._index_ready:
            return

        with self._index_lock:
            if self._index_ready:
                return

            response = self._request('HEAD', f'/{self._index_name}', raise_for_status=False)
            if response.status_code == 404:
                self._request(
                    'PUT',
                    f'/{self._index_name}',
                    json_body={
                        'mappings': {
                            'properties': {
                                'id': {'type': 'keyword'},
                                'created_at': {'type': 'date'},
                                'user_id': {'type': 'keyword'},
                                'user_email': {'type': 'keyword'},
                                'search_scope': {'type': 'keyword'},
                                'genre': {'type': 'keyword'},
                                'emotions': {'type': 'keyword'},
                                'mood_tags': {'type': 'keyword'},
                                'search_keywords': {'type': 'keyword'},
                                'request_keywords': {'type': 'keyword'},
                                'blocked_mood_tags': {'type': 'keyword'},
                            }
                        }
                    },
                )

            self._index_ready = True

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, object] | None = None,
        raise_for_status: bool = True,
    ) -> requests.Response:
        url = f'{self._endpoint}{path}'
        body = b''
        headers: dict[str, str] = {}
        if json_body is not None:
            body = json.dumps(json_body, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        credentials = self._credentials_provider.get_credentials()
        signed_headers = self._signer.sign(method, url, credentials, body=body, headers=headers)
        response = requests.request(method, url, headers=signed_headers, data=body, timeout=20)
        if raise_for_status:
            response.raise_for_status()
        return response


_repository: SearchRecordRepository
if os.getenv('OPENSEARCH_ENDPOINT'):
    _repository = OpenSearchSearchRecordRepository()
else:
    _repository = InMemorySearchRecordRepository()


def save_search_record(record: SearchRecord) -> SearchRecord:
    return _repository.save(record)


def list_search_records(user_id: str | None = None) -> list[SearchRecord]:
    return _repository.list(user_id)
