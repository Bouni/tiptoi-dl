import json
import logging
import re
import sys
import time
from pathlib import Path

import httpx
from selectolax.lexbor import LexborHTMLParser

BASEPATH = Path(__file__).resolve().parents[2]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
LOGGER = logging.getLogger("TipToiCatalog")


class TipToiCatalog:
    def __init__(self, target: str = ""):
        self.base_url = (
            "https://service.ravensburger.de/tiptoi%C2%AE/tiptoi%C2%AE_Audiodateien"
        )
        self.catalog = []
        self.products = []
        self.client = httpx.Client(timeout=10, follow_redirects=True)
        LOGGER.info("Start data scraping")
        self.get_catalog(target)
        for product in self.catalog:
            self.products.extend(self.get_product_data(product))
            time.sleep(0.1)
        self.persist_products()

    def get_catalog(self, target):
        r = self.client.get(self.base_url)
        LOGGER.info(f"Status code: {r.status_code}")
        tree = LexborHTMLParser(r.text)
        links = [
            link.attributes
            for link in tree.css("a.mt-listing-detailed-subpage-title")
        ]
        LOGGER.info(f"Found {len(links)} links")
        for link in links:
            if target:
                if target in link.get("title"):
                    self.catalog.append(
                        {"title": link.get("title"), "url": link.get("href")}
                    )
            else:
                self.catalog.append(
                    {"title": link.get("title"), "url": link.get("href")}
                )

    def sanitize_title(self, product: dict) -> dict:
        product["title"] = re.sub(r"\s\d{5}.*$", "", product["title"])
        product["title"] = product["title"].replace("tiptoi®", "")
        product["title"] = product["title"].replace(
            "Audiodatei", ""
        )  # ravensburger typo *shrug*
        product["title"] = product["title"].replace(
            "Audioatei", ""
        )  # ravensburger typo *shrug*
        product["title"] = product["title"].replace("\xa0", " ")
        product["title"] = product["title"].strip()
        return product

    def get_product_numbers(self, product: dict) -> dict:
        numbers = re.findall(r"\d{5}", product["title"])

        product["numbers"] = numbers
        return product

    def get_product_image(self, img: str | None) -> str:
        if img:
            url = img.split("?")[0]
            return url
        return ""

    def get_product_data(self, product: dict) -> list[dict]:
        product = self.get_product_numbers(product)
        product = self.sanitize_title(product)
        LOGGER.info(f"Get product data for {product['title']}")
        product_data = []

        r = self.client.get(product["url"])
        LOGGER.info(f"Status code: {r.status_code}")

        tree = LexborHTMLParser(r.text)
        links = tree.css('a[href*=".gme"]')

        for n, link in enumerate(links):
            data = {}
            data["gme"] = link.attributes.get("href")
            data["title"] = product["title"]
            data["number"] = ""
            if product["numbers"]:
                try:
                    data["number"] = product["numbers"][n]
                except IndexError:
                    LOGGER.warning(
                        "Inconsitent data for %s, catalog maybe not 100%% complete",
                        data["title"],
                    )
            img = link.css_first("img")
            if img is not None:
                data["img"] = self.get_product_image(img.attributes.get("src"))
            product_data.append(data)
        return product_data

    def persist_products(self):
        LOGGER.info("Write json file")
        (BASEPATH / "output").mkdir(exist_ok=True)
        with open(BASEPATH / "output/products.json", "w") as f:
            json.dump(self.products, f)


if __name__ == "__main__":
    TipToiCatalog(sys.argv[1] if len(sys.argv) == 2 else "")
