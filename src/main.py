#!/usr/bin/env python
import logging
from pathlib import Path
from typing import ClassVar, cast

import psutil
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.color import Gradient
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    ProgressBar,
    Static,
)
from textual.widgets.button import ButtonVariant

from api import TipToiAPI

logger = logging.getLogger(__name__)


class RainbowProgress(ProgressBar):
    def __init__(
        self,
        total: float | None = 100,
        show_eta: bool = True,
        show_percentage: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            total=total,
            gradient=Gradient.from_colors(
                "#881177",
                "#aa3355",
                "#cc6666",
                "#ee9944",
                "#eedd00",
                "#99dd55",
                "#44dd88",
                "#22ccbb",
                "#00bbcc",
                "#0099cc",
                "#3366bb",
                "#663399",
            ),
            show_eta=show_eta,
            show_percentage=show_percentage,
            **kwargs,
        )


class CatalogTable(DataTable):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+d",
            "download_selected",
            "Download selected file",
            key_display="Ctrl+d",
            show=True,
        ),
    ]

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "download_selected":
            return self.cursor_row is not None
        return True

    def action_download_selected(self) -> None:
        row_key, _ = self.coordinate_to_cell_key(self.cursor_coordinate)
        app = cast("TipToiDlApp", self.app)
        item_id = self.get_cell(row_key, app.col_id)
        app.download_item(item_id)


class InfoScreen(ModalScreen[None]):
    CSS = """
    InfoScreen {
        align: center middle;
    }

    #info_dialog {
        width: 100;
        height: auto;
        background: $surface;
        padding: 1 2;
    }

    /* Dynamic borders based on mode */
    #info_dialog.mode-error { border: thick $error 80%; }
    #info_dialog.mode-warning { border: thick $warning 80%; }
    #info_dialog.mode-info { border: thick $accent 80%; }

    #info_title {
        text-style: bold;
        margin-bottom: 1;
    }

    /* Dynamic title colors */
    .mode-error #info_title { color: $error; }
    .mode-warning #info_title { color: $warning; }
    .mode-info #info_title { color: $accent; }

    #info_message {
        margin-bottom: 1;
    }

    #info_dismiss {
        width: 100%;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "dismiss", "Close", show=False),
    ]

    MODE_CONFIGS: ClassVar[dict[str, tuple[str, ButtonVariant]]] = {
        "error": ("Error", "error"),
        "warning": ("Warning", "warning"),
        "info": ("Information", "primary"),
    }

    def __init__(
        self,
        message: str,
        title: str | None = None,
        mode: str = "info",
    ) -> None:
        super().__init__()
        self.message = message
        self.mode = mode.lower() if mode.lower() in self.MODE_CONFIGS else "info"
        default_title, variant = self.MODE_CONFIGS[self.mode]
        self.button_variant: ButtonVariant = variant
        self.dialog_title = title or default_title

    def compose(self) -> ComposeResult:
        with Vertical(id="info_dialog", classes=f"mode-{self.mode}"):
            yield Static(self.dialog_title, id="info_title")
            yield Static(self.message, id="info_message")
            yield Button("OK", id="info_dismiss", variant=self.button_variant)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class TipToiDlApp(App):
    ENABLE_COMMAND_PALETTE = False

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            key_display="Ctrl+q",
            tooltip="Quit the app and return to the command prompt.",
            show=True,
            priority=True,
        ),
    ]

    CSS = """
    ProgressBar {
        width: 100%;
    }

    Bar {
        width: 1fr;
    }

    #status_label {
        width: 100%;
        margin-bottom: 1;
        content-align: center middle;
    }

    #search_input {
        width: 100%;
        margin-bottom: 1;
    }

    #catalog_table {
        width: 100%;
        height: 1fr;
    }
    """

    def on_mount(self) -> None:
        self.theme = "nord"
        self.title = "TipToiDl"
        self.api = TipToiAPI()
        self.catalog_items: list[dict] = []
        self.run_worker(self.load_catalog(), exclusive=True)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Vertical():
            yield RainbowProgress(total=50, show_eta=False, id="progress_bar")
            yield Static("Download catalog", id="status_label")
            yield Input(placeholder="Search…", id="search_input")
            yield CatalogTable(id="catalog_table")

    async def on_unmount(self) -> None:
        """Clean up the API client when the app closes."""
        await self.api.aclose()

    async def load_catalog(self) -> None:
        """Fetch data from the API and update progress as we go."""
        bar = self.query_one("#progress_bar", RainbowProgress)
        label = self.query_one("#status_label", Static)
        table = self.query_one("#catalog_table", DataTable)

        label.update("Download catalog")

        timer = self.set_interval(
            1 / 20, lambda: bar.advance(1) if bar.progress < 90 else None
        )

        try:
            catalog = await self.api.get_catalog()
        finally:
            timer.stop()

        if not catalog:
            logger.error("Catalog was empty")
            label.update("Error downloading catalog ✗")
            return

        bar.progress = 100
        label.update(f"Download catalog ✓ ({len(catalog.get('products', []))})")

        self.catalog_items = catalog.get("products", [])

        table.add_columns("Name", "ID", "Categories", "Age", "Description")
        (
            self.col_name,
            self.col_id,
            self.col_categories,
            self.col_age,
            self.col_description,
        ) = table.columns.keys()
        self._populate_table(self.catalog_items)

    def _get_age_range(self, item: dict) -> str:
        fromAge = item.get("ageFrom")
        toAge = item.get("ageTo")
        if fromAge and toAge:
            return f"from {fromAge} to {toAge}"
        if not fromAge and toAge:
            return f"up to {toAge}"
        if fromAge and not toAge:
            return f"from {fromAge}"
        return ""

    def _populate_table(self, items: list[dict]) -> None:
        """Clear and refill the table with the given items."""
        table = self.query_one("#catalog_table", DataTable)
        table.clear()
        for item in items:
            table.add_row(
                item.get("name", ""),
                item.get("id", ""),
                ", ".join(item.get("categories", [])),
                self._get_age_range(item),
                item.get("description", ""),
            )
        table.sort(self.col_id, self.col_categories)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the table as the user types in the search box."""
        if event.input.id != "search_input":
            return

        query = event.value.strip().lower()
        if not query:
            self._populate_table(self.catalog_items)
            return

        filtered = [
            item
            for item in self.catalog_items
            if query in item.get("name", "").lower()
            or query in str(item.get("id", "")).lower()
        ]
        self._populate_table(filtered)

    def download_item(self, item_id: str) -> None:
        item = next(
            (i for i in self.catalog_items if str(i.get("id")) == str(item_id)), None
        )
        if item is None:
            return
        game_files = item.get("gameFiles", [])
        if not game_files:
            return
        url = game_files[0]["url"]
        filename = game_files[0]["fileName"]
        self.run_worker(self._download_file(url, filename), exclusive=True)

    async def _download_file(self, url: str, filename: str) -> None:
        bar = self.query_one("#progress_bar", RainbowProgress)
        label = self.query_one("#status_label", Static)

        disk = self.find_tiptoi_disk()
        path = (Path(disk) / filename if disk else Path.home() / filename).resolve()

        label.update(f"Downloading {path!s}…")
        bar.progress = 0

        def on_progress(downloaded: int, total: int) -> None:
            bar.total = total or None
            bar.progress = downloaded

        async with TipToiAPI() as api:
            await api.get_audiofile(url, str(path), on_progress=on_progress)
            label.update(f"Downloaded {path!s} ✓")
            self.push_screen(InfoScreen(f"Downloaded {path!s} ✓"))

    def find_tiptoi_disk(self) -> str:
        disks = [
            p.mountpoint
            for p in psutil.disk_partitions(all=True)
            if "/dev/" in p.device.lower() and "toi" in p.mountpoint.lower()
        ]
        if len(disks) == 1:
            return disks[0]
        else:
            self.push_screen(InfoScreen("No TipToi found, save to ."))
            return "."


def main():
    app = TipToiDlApp()
    app.run()


if __name__ == "__main__":
    main()
