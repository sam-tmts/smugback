"""Talking to SmugMug: OAuth 1.0a sign-in, then read-only API requests.

See ADR-0006: after sign-in the client can only send GET requests, and OAuth
signatures travel in the Authorization header, never in URLs.
"""

import json
import urllib.error
import urllib.request
from collections.abc import Iterator
from urllib.parse import parse_qs, urlencode

from oauthlib.oauth1 import Client

from smugback.credentials import Credentials

API_HOST = "https://api.smugmug.com"
OAUTH_URL = f"{API_HOST}/services/oauth/1.0a"
PAGE_SIZE = 100


class SmugMugError(Exception):
    """A request to SmugMug failed. The message never contains secrets."""


def fetch(method: str, url: str, headers: dict) -> tuple[int, bytes]:
    """Send one HTTP request. Tests replace this, so they never reach SmugMug."""
    data = b"" if method == "POST" else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()
    except urllib.error.URLError as error:
        raise SmugMugError(f"Couldn't reach SmugMug: {error.reason}") from None


def _token_request(client: Client, url: str, step: str) -> tuple[str, str]:
    # The OAuth spec recommends POST for token requests; they change nothing
    # in the account
    signed_url, headers, _ = client.sign(url, http_method="POST")
    status, body = fetch("POST", signed_url, headers)
    if status != 200:
        raise SmugMugError(f"SmugMug refused the {step} (HTTP {status}).")
    reply = parse_qs(body.decode())
    try:
        return reply["oauth_token"][0], reply["oauth_token_secret"][0]
    except KeyError:
        raise SmugMugError(f"SmugMug's reply to the {step} was incomplete.") from None


def get_request_token(api_key: str, api_secret: str) -> tuple[str, str]:
    client = Client(api_key, client_secret=api_secret, callback_uri="oob")
    return _token_request(client, f"{OAUTH_URL}/getRequestToken", "sign-in request")


def authorize_url(request_token: str) -> str:
    # Full access includes private albums; Read permission keeps it read-only
    query = urlencode(
        {"oauth_token": request_token, "Access": "Full", "Permissions": "Read"}
    )
    return f"{OAUTH_URL}/authorize?{query}"


def get_access_token(
    api_key: str, api_secret: str, request_token: str, request_secret: str, pin: str
) -> tuple[str, str]:
    client = Client(
        api_key,
        client_secret=api_secret,
        resource_owner_key=request_token,
        resource_owner_secret=request_secret,
        verifier=pin,
    )
    return _token_request(client, f"{OAUTH_URL}/getAccessToken", "sign-in code")


class SmugMug:
    """A signed-in, read-only SmugMug API client: it has only `get`."""

    def __init__(self, credentials: Credentials):
        self._client = Client(
            credentials.api_key,
            client_secret=credentials.api_secret,
            resource_owner_key=credentials.token,
            resource_owner_secret=credentials.token_secret,
        )

    def get(self, path: str, params: dict | None = None) -> dict:
        # Only paths on SmugMug's API host, so the signed Authorization header
        # can't be sent anywhere else
        if not path.startswith("/"):
            raise SmugMugError("SmugMug sent an unexpected link.")
        url = API_HOST + path
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        signed_url, headers, _ = self._client.sign(url, http_method="GET")
        headers["Accept"] = "application/json"
        status, body = fetch("GET", signed_url, headers)
        if status == 401:
            raise SmugMugError(
                "SmugMug refused SmugBack's access (HTTP 401). If you revoked it, "
                "run `smugback login` again."
            )
        if status != 200:
            raise SmugMugError(f"SmugMug returned HTTP {status}.")
        return json.loads(body)

    def albums(self) -> Iterator[dict]:
        """Every album in the signed-in account, across all pages."""
        user = self.get("/api/v2!authuser")["Response"]["User"]
        page = self.get(
            user["Uris"]["UserAlbums"]["Uri"], {"start": 1, "count": PAGE_SIZE}
        )
        while True:
            response = page["Response"]
            yield from response.get("Album", [])
            next_page = response.get("Pages", {}).get("NextPage")
            if not next_page:
                return
            page = self.get(next_page)
