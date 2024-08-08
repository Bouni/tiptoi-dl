import re
import sys
import requests
from pathlib import Path
import psutil
from bs4 import BeautifulSoup


class TipToiDL:
    def __init__(self):
        self.base_url = (
            "https://service.ravensburger.de/tiptoi%C2%AE/tiptoi%C2%AE_Audiodateien"
        )
        self.catalog = []
        self.results = []
        self.main()

    def main(self):
        print("=" * 80)
        print("\nWelcome to TipToi-dl, a CLI TipToi audio file downloader.\n")
        print("=" * 80)
        print("  Downloading Catalog ...")
        self.get_catalog()
        print(f"  Found {len(self.catalog)} files\n")
        while True:
            self.results = []
            s = input("Enter search term or 'q' to quit: ")
            if s == "q":
                break
            if s != "":
                self.search(s)
            if len(self.results) == 0:
                print("  No results found")
                continue
            print(f"  Found {len(self.results)} results!\n")
            for n, r in enumerate(self.results, 1):
                print(f"  [{n}] {r["title"]}")
            print("\n")
            s = input("Select item by entering number, q to quit: ")
            if s == "q":
                break
            try:
                n = int(s)
            except ValueError:
                print("  Not a vaild selection, quit ...")
                sys.exit(1)
            if n < 0 or n > len(self.results):
                print("  Not a valid selection, quit ...")
                break
            print(f"  Your selection: {self.results[n-1]['title']}")
            self.get_product_page(self.results[n - 1])

    def get_catalog(self):
        r = requests.get(self.base_url)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", class_="mt-listing-detailed-subpage-title")
        for link in links:
            self.catalog.append({"title": link.get("title"), "url": link.get("href")})

    def get_product_page(self, product: dict):
        r = requests.get(product["url"])
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all(
            "a",
            href=re.compile("gme"),
        )
        subresults = []
        if len(links) == 1:
            title = links[0].find_next("p").span.strong.string
            print(f"  Download {title} audio file now")
            self.download(links[0].get("href"))
        else:
            print("  This product has multiple variants")
            for n, link in enumerate(links, 1):
                tr = link.parent.parent.find_next("tr")
                td = tr.find_all("td")
                title = td[n - 1].strong.string
                subresults.append({"title": title, "url": link.get("href")})
                print(f"  [{n}] {title}")
            print("\n")
            s = input("Select item by entering number, q to quit: ")
            if s == "q":
                sys.exit()
            try:
                n = int(s)
            except ValueError:
                print("  Not a vaild selection, quit ...")
                sys.exit(1)
            if n < 0 or n > len(subresults):
                print("  Not a valid selection, quit ...")
                sys.exit()
            print(f"  Your selection: {subresults[n-1]['title']}")
            print(f"  Download {subresults[n-1]['title']} audio file now")
            self.download(subresults[n - 1]["url"])

    def search(self, searchterm: str):
        for item in self.catalog:
            if searchterm.lower() in item["title"].lower():
                self.results.append(item)

    def download(self, url: str):
        print(f"  Download {url}")
        filename = url.split("/")[-1]
        disk = self.find_tiptoi_disk()
        if not disk:
            path = Path.home() / filename
        else:
            path = Path(disk) / filename
        print(f"  Download file to {path}")
        with requests.get(url, stream=True) as r:
            with open(path, mode="wb") as f:
                f.write(r.content)
        sys.exit()

    def find_tiptoi_disk(self):
        disks = [
            p.mountpoint
            for p in psutil.disk_partitions(all=True)
            if "/dev/" in p.device.lower() and "toi" in p.mountpoint.lower()
        ]
        if len(disks) == 1:
            return disks[0]
        else:
            print("  Cannot find tiptoi disk ...")
            return None


if __name__ == "__main__":
    ttdl = TipToiDL()
