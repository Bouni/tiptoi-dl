import logging
import time
from collections.abc import Callable
from typing import Literal, Self

import anyio
import httpx

logger = logging.getLogger(__name__)

# OAuth client credentials of the official tiptoi Manager app
CLIENT_ID = "tiptoi-manager-v2"
CLIENT_SECRET = "CYmWkYyhY3traWuGd5cHcNV"
TOKEN_URL = "https://oauth.ravensburger.com/oauth/token"

languages = Literal["de_DE", "nl_NL", "fr_FR", "it_IT", "ru_RU"]


class TipToiAPI:
    def __init__(self, jwt: str | None = None):
        self.jwt = jwt
        self.jwt_expires_at = float("inf") if jwt else 0.0
        self.base_url = "https://ttapiv2.ravensburger.com/api/v2"
        self.client = httpx.AsyncClient(
            headers={
                "Host": "ttapiv2.ravensburger.com",
                "Accept": "*/*",
                "User-Agent": "tiptoiManager/5.2",
                "X-Unity-Version": "2021.3.30f1",
            }
        )
        if jwt:
            self.client.headers["Authorization"] = f"Bearer {jwt}"
        self.file_client = httpx.AsyncClient(
            headers={
                "Accept": "*/*",
                "User-Agent": "tiptoiManager/5.2",
            }
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self.client.aclose()
        await self.file_client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.aclose()

    async def _ensure_token(self) -> None:
        """Fetch a new bearer token if there is none or it is about to expire."""
        if time.monotonic() < self.jwt_expires_at:
            return
        r = await self.client.post(
            TOKEN_URL,
            headers={"Host": "oauth.ravensburger.com"},
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )
        r.raise_for_status()
        token = r.json()
        self.jwt = token["access_token"]
        # Refresh a minute early to avoid using a token right as it expires
        self.jwt_expires_at = time.monotonic() + token.get("expires_in", 0) - 60
        self.client.headers["Authorization"] = f"Bearer {self.jwt}"

    async def get_catalog(self, language: languages = "de_DE") -> dict:
        await self._ensure_token()
        r = await self.client.get(f"{self.base_url}/catalog/{language}")
        if r.is_success:
            return r.json()
        logger.error("Failed to fetch catalog: %s", r.status_code)
        return {}

    async def get_audiofile(
        self,
        url: str,
        filename: str,
        on_progress: Callable[[int, int], None] | None = None,
    ):
        async with self.file_client.stream("GET", url) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            async with await anyio.open_file(filename, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    await f.write(chunk)
                    downloaded += len(chunk)
                    if on_progress:
                        on_progress(downloaded, total)

    # async def get_firmware_updates(self, language: languages = "de_DE") -> dict:
    #     r = await self.file_client.get(f"{self.base_url}/config/{language}/WIN")
    #     if r.is_success:
    #         return r.json()
    #     logging.error("Failed to fetch firmware info: %s", r.status_code)
    #     return {}


def main():
    import asyncio

    async def run() -> None:
        async with TipToiAPI() as api:
            catalog = await api.get_catalog()
            print(f"Catalog entries: {len(catalog)}")
            if itemdata := catalog.get("products", []):
                print(len(itemdata))
                itemdata = itemdata[int(len(itemdata) / 2)]
                print(itemdata)
                await api.get_audiofile(
                    itemdata.get("gameFiles", {})[0].get("url"),
                    itemdata.get("gameFiles", {})[0].get("fileName"),
                )

    asyncio.run(run())


if __name__ == "__main__":
    main()
