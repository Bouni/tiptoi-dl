import logging
import os
from typing import Literal

import requests

JWT = os.getenv("RAVENSBURGER_JWT", "")


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
