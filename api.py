import logging
from typing import Literal

import requests

JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsidGlwdG9pIl0sInNjb3BlIjpbInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE3NzAzNzk1NjcsImF1dGhvcml0aWVzIjpbIlJPTEVfQ0xJRU5UIl0sImp0aSI6IjU0NDE1MzFlLTUwNTEtNGI3MC04MDZkLTY0NTM1NzUxZmJlZiIsImNsaWVudF9pZCI6InRpcHRvaS1tYW5hZ2VyLXYyIn0.jvQpiQJp577NTMBbiOkyBIKSt_OYIBi4fLuKJBOQAX69U7S1DwQBeilx40MsTUDNcDRagfYGmUSqPxn4ahhJ4MRtLxUjxoz932p3oR9mvI5-gUkgL03KwNNKj0ShQ2z0AJY1YlUmJJdp-DokzkLbe20X-ad-fqctxtUFEaQ6kxv-G6fAk2sOEkTQf9Gg4z37s6l2XtRFk7YfwhEuvvPHg-qTzEV45IMZQtiuDb9FESZF5Fu44zFcxmpBm-3sK_tCAlsoF4J9x47OSxq4wWdvkSgqCYg0pp0jBXfFKe3qsiLJNjdzM22LShgwf3jlU74b6NnkLodEsQE1XE0TS9vkew"


class TipToiAPI:
    def __init__(self):
        self.base_url = "https://ttapiv2.ravensburger.com/api/v2"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Host": "ttapiv2.ravensburger.com",
                "Accept": "*/*",
                "Authorization": f"Bearer {JWT}",
                "User-Agent": "tiptoiManager/5.2",
                "X-Unity-Version": "2021.3.30f1",
            }
        )

    def get_catalog(
        self, language: Literal["de_DE", "nl_NL", "fr_FR", "it_IT", "ru_RU"] = "de_DE"
    ) -> dict:
        r = self.session.get(f"{self.base_url}/catalog/{language}")
        if r.ok:
            return r.json()
        logging.error("Failed to fetch catalog: %", r.status_code)
        return {}

    def get_audiofile(self, url: str, filename: str):
        with requests.get(
            url,
            stream=True,
        ) as response:
            response.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    def get_firmware_updates(
        self, language: Literal["de_DE", "nl_NL", "fr_FR", "it_IT", "ru_RU"] = "de_DE"
    ) -> dict:
        r = self.session.get(f"{self.base_url}/config/{language}/WIN")
        if r.ok:
            return r.json()
        logging.error("Failed to fetch firmware info: %", r.status_code)
        return {}


def main():
    ttapi = TipToiAPI()
    catalog = ttapi.get_catalog("nl_NL")
    if itemdata := catalog.get("products", []):
        itemdata = itemdata[200]
        ttapi.get_audiofile(
            itemdata.get("gameFiles", {})[0].get("url"),
            itemdata.get("gameFiles", {})[0].get("fileName"),
        )


if __name__ == "__main__":
    main()
