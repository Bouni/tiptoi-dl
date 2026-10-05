import logging
from collections.abc import Callable
from typing import Literal, Self

import anyio
import httpx

logger = logging.getLogger(__name__)

# Bearer token of the official tiptoi Manager app
JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsidGlwdG9pIl0sInNjb3BlIjpbInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE3NzAzNzk1NjcsImF1dGhvcml0aWVzIjpbIlJPTEVfQ0xJRU5UIl0sImp0aSI6IjU0NDE1MzFlLTUwNTEtNGI3MC04MDZkLTY0NTM1NzUxZmJlZiIsImNsaWVudF9pZCI6InRpcHRvaS1tYW5hZ2VyLXYyIn0.jvQpiQJp577NTMBbiOkyBIKSt_OYIBi4fLuKJBOQAX69U7S1DwQBeilx40MsTUDNcDRagfYGmUSqPxn4ahhJ4MRtLxUjxoz932p3oR9mvI5-gUkgL03KwNNKj0ShQ2z0AJY1YlUmJJdp-DokzkLbe20X-ad-fqctxtUFEaQ6kxv-G6fAk2sOEkTQf9Gg4z37s6l2XtRFk7YfwhEuvvPHg-qTzEV45IMZQtiuDb9FESZF5Fu44zFcxmpBm-3sK_tCAlsoF4J9x47OSxq4wWdvkSgqCYg0pp0jBXfFKe3qsiLJNjdzM22LShgwf3jlU74b6NnkLodEsQE1XE0TS9vkew"

languages = Literal["de_DE", "nl_NL", "fr_FR", "it_IT", "ru_RU"]


class TipToiAPI:
    def __init__(self, jwt: str | None = None):
        jwt = jwt or JWT
        self.base_url = "https://ttapiv2.ravensburger.com/api/v2"
        self.client = httpx.AsyncClient(
            headers={
                "Host": "ttapiv2.ravensburger.com",
                "Accept": "*/*",
                "Authorization": f"Bearer {jwt}",
                "User-Agent": "tiptoiManager/5.2",
                "X-Unity-Version": "2021.3.30f1",
            }
        )
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

    async def get_catalog(self, language: languages = "de_DE") -> dict:
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
