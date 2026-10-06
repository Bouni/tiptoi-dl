#!/usr/bin/env python
import logging
from pathlib import Path
from typing import ClassVar, cast

import psutil
from rich.cells import cell_len
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.color import Gradient
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.theme import Theme
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    ProgressBar,
    Static,
)
from textual.widgets.button import ButtonVariant

from api import TipToiAPI, languages

logger = logging.getLogger(__name__)


# Colors inspired by Charm's lipgloss / bubbles defaults
CHARM_THEME = Theme(
    name="charm",
    primary="#7D56F4",
    secondary="#EE6FF8",
    accent="#FF5FAF",
    success="#04B575",
    warning="#FFB86C",
    error="#FF4672",
    foreground="#DDDDDD",
    background="#171717",
    surface="#171717",
    panel="#2A2A2A",
    dark=True,
    variables={
        "footer-background": "transparent",
        "footer-item-background": "transparent",
        "footer-key-background": "transparent",
        "footer-key-foreground": "#909090",
        "footer-description-foreground": "#777777",
        "block-cursor-background": "#7D56F4",
        "block-cursor-foreground": "#FFFFFF",
        "block-cursor-blurred-background": "#3C3C3C",
        "input-cursor-background": "#FF5FAF",
        "input-selection-background": "#7D56F4 40%",
        "border": "#FF5FAF",
        "border-blurred": "#3C3C3C",
    },
)


class GradientProgress(ProgressBar):
    def __init__(
        self,
        total: float | None = 100,
        show_eta: bool = True,
        show_percentage: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            total=total,
            gradient=Gradient.from_colors("#5A56E0", "#EE6FF8"),
            show_eta=show_eta,
            show_percentage=show_percentage,
            **kwargs,
        )


class Spinner(Static):
    """A bubbles-style dot spinner that can settle into a final state."""

    FRAMES = "⣾⣽⣻⢿⡿⣟⣯⣷"

    def on_mount(self) -> None:
        self._frame = 0
        self._timer = self.set_interval(1 / 12, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(self.FRAMES)
        self.update(self.FRAMES[self._frame])

    def spin(self) -> None:
        self.set_classes("")
        self._timer.resume()

    def done(self, ok: bool = True) -> None:
        self._timer.pause()
        self.set_classes("-ok" if ok else "-fail")
        self.update("✓" if ok else "✗")


class SearchInput(Input):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "tab",
            "app.focus_next",
            "Go to table",
            key_display="Tab",
            show=True,
        ),
    ]


class CatalogTable(DataTable):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "enter",
            "show_details",
            "Show details",
            key_display="Enter",
            show=True,
        ),
        Binding(
            "ctrl+d",
            "download_selected",
            "Download selected file",
            key_display="Ctrl+d",
            show=True,
        ),
    ]

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action in ("download_selected", "show_details"):
            return self.row_count > 0
        return True

    def _selected_item_id(self) -> str:
        row_key, _ = self.coordinate_to_cell_key(self.cursor_coordinate)
        app = cast("TipToiDlApp", self.app)
        return self.get_cell(row_key, app.col_id)

    def action_download_selected(self) -> None:
        cast("TipToiDlApp", self.app).download_item(self._selected_item_id())

    def action_show_details(self) -> None:
        cast("TipToiDlApp", self.app).show_details(self._selected_item_id())

    def on_resize(self, event: events.Resize) -> None:
        cast("TipToiDlApp", self.app).fit_description_column()


class LanguageFlag(Static):
    """A clickable flag that switches the catalog language.

    Flags are drawn with block characters instead of emoji, which many
    terminals can't display.
    """

    # (stripe direction, stripe colors from top/left to bottom/right)
    FLAGS: ClassVar[dict[str, tuple[str, tuple[str, str, str]]]] = {
        "de_DE": ("horizontal", ("#000000", "#DD0000", "#FFCE00")),
        "nl_NL": ("horizontal", ("#AE1C28", "#FFFFFF", "#21468B")),
        "fr_FR": ("vertical", ("#0055A4", "#FFFFFF", "#EF4135")),
        "it_IT": ("vertical", ("#009246", "#FFFFFF", "#CE2B37")),
        "ru_RU": ("horizontal", ("#FFFFFF", "#0039A6", "#D52B1E")),
    }

    def __init__(self, language: languages) -> None:
        super().__init__(self._draw(*self.FLAGS[language]), classes="language_flag")
        self.language: languages = language
        self.tooltip = language
        self.border_subtitle = language[-2:]

    @staticmethod
    def _draw(direction: str, colors: tuple[str, str, str]) -> Text:
        """Draw a tricolor flag that is six cells wide and two rows high."""
        first, middle, last = colors
        if direction == "vertical":
            row = Text.assemble(*(("  ", f"on {color}") for color in colors))
            return Text("\n").join([row, row.copy()])
        # Split two rows into stripes of 5/16, 6/16 and 5/16 using lower eighth
        # blocks
        return Text("\n").join(
            [
                Text("▃" * 6, style=f"{middle} on {first}"),
                Text("▅" * 6, style=f"{last} on {middle}"),
            ]
        )

    def on_click(self) -> None:
        cast("TipToiDlApp", self.app).set_language(self.language)


class DetailScreen(ModalScreen[None]):
    CSS = """
    DetailScreen {
        align: center middle;
    }

    #detail_dialog {
        width: 80%;
        max-width: 100;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: round $accent;
        border-title-color: $accent;
        border-title-style: bold;
        border-title-align: left;
        padding: 1 2;
    }

    .detail_row {
        height: auto;
    }

    .detail_label {
        width: 14;
        color: $secondary;
        text-style: bold;
    }

    .detail_value {
        width: 1fr;
    }

    #detail_description {
        height: auto;
        max-height: 20;
        margin-top: 1;
        scrollbar-size: 1 1;
        scrollbar-background: $surface;
        scrollbar-color: #3C3C3C;
        scrollbar-color-hover: $primary;
        scrollbar-color-active: $accent;
    }

    DetailScreen Footer {
        padding: 0 2;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "dismiss", "Close", key_display="Enter", show=True),
        Binding("escape", "dismiss", "Close", show=False),
    ]

    def __init__(self, item: dict, age_range: str) -> None:
        super().__init__()
        self.item = item
        self.age_range = age_range

    def _fields(self) -> list[tuple[str, str | Text]]:
        item = self.item
        game_files = item.get("gameFiles", [])
        game_file = game_files[0] if game_files else {}
        shop_url = item.get("shopUrl", "")
        return [
            ("ID", str(item.get("id", ""))),
            ("Categories", ", ".join(item.get("categories", []))),
            ("Age", self.age_range),
            ("Released", item.get("releaseDate", "")[:10]),
            ("File", game_file.get("fileName", "")),
            ("Version", game_file.get("version", "")),
            ("Shop", Text(shop_url, style=f"link {shop_url}") if shop_url else ""),
        ]

    def compose(self) -> ComposeResult:
        with Vertical(id="detail_dialog") as dialog:
            dialog.border_title = f" {self.item.get('name', '')} "
            for label, value in self._fields():
                if not value:
                    continue
                with Horizontal(classes="detail_row"):
                    yield Static(label, classes="detail_label")
                    yield Static(value, classes="detail_value", markup=False)
            with VerticalScroll(id="detail_description"):
                yield Static(
                    self.item.get("description", "").strip() or "No description.",
                    markup=False,
                )
        yield Footer()


class InfoScreen(ModalScreen[None]):
    CSS = """
    InfoScreen {
        align: center middle;
    }

    #info_dialog {
        width: auto;
        max-width: 80%;
        min-width: 40;
        height: auto;
        background: $surface;
        padding: 1 3;
        border-title-style: bold;
        border-title-align: left;
    }

    /* Dynamic borders based on mode */
    #info_dialog.mode-error { border: round $error; border-title-color: $error; }
    #info_dialog.mode-warning { border: round $warning; border-title-color: $warning; }
    #info_dialog.mode-info { border: round $accent; border-title-color: $accent; }

    #info_message {
        width: auto;
        margin-bottom: 1;
    }

    #info_buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }

    #info_dismiss {
        min-width: 10;
        background: $primary;
        color: #FFFDF5;
        text-style: bold;
        &:focus, &:hover {
            background: $accent;
            text-style: bold;
        }
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
        with Vertical(id="info_dialog", classes=f"mode-{self.mode}") as dialog:
            dialog.border_title = f" {self.dialog_title} "
            yield Static(self.message, id="info_message")
            with Horizontal(id="info_buttons"):
                yield Button(
                    "OK", id="info_dismiss", variant=self.button_variant, compact=True
                )

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
        Binding(
            "ctrl+l",
            "next_language",
            "Switch language",
            key_display="Ctrl+l",
            show=True,
        ),
    ]

    CSS = """
    Screen#_default {
        padding: 1 2 0 2;
    }

    #title_bar {
        height: 1;
        margin-bottom: 1;
    }

    #title {
        width: auto;
        padding: 0 1;
        background: $primary;
        color: #FFFDF5;
        text-style: bold;
    }

    #subtitle {
        width: 1fr;
        padding-left: 1;
        color: #626262;
    }

    #search_input, #catalog_table {
        background: $surface;
        border: round $border-blurred;
        border-title-color: #626262;
        border-subtitle-color: #626262;
        padding: 0 1;
    }

    #search_input:focus, #catalog_table:focus {
        border: round $accent;
        border-title-color: $accent;
        border-title-style: bold;
    }

    #search_input {
        margin-bottom: 0;
    }

    #search_input > .input--placeholder {
        color: #4A4A4A;
    }

    #catalog_table {
        height: 1fr;
        scrollbar-size: 1 1;
        scrollbar-background: $surface;
        scrollbar-background-hover: $surface;
        scrollbar-background-active: $surface;
        scrollbar-color: #3C3C3C;
        scrollbar-color-hover: $primary;
        scrollbar-color-active: $accent;
        scrollbar-corner-color: $surface;
        &:focus { background-tint: 0%; }
        & > .datatable--header {
            background: $surface;
            color: $secondary;
            text-style: bold;
        }
        &:focus > .datatable--header { background-tint: 0%; }
        & > .datatable--even-row { background: $surface; }
        &:dark > .datatable--even-row { background: #1E1E1E; }
        & > .datatable--hover { background: $primary 20%; }
        & > .datatable--header-hover { background: $surface; }
    }

    #status_bar {
        height: 1;
        margin: 1 0;
    }

    Spinner {
        width: 2;
        color: $accent;
        &.-ok { color: $success; }
        &.-fail { color: $error; }
    }

    #status_label {
        width: 1fr;
        color: #A0A0A0;
        text-wrap: nowrap;
        text-overflow: ellipsis;
    }

    GradientProgress {
        width: auto;
    }

    GradientProgress Bar {
        width: 30;
        & > .bar--bar, & > .bar--complete { background: #3C3C3C; }
    }

    GradientProgress #percentage {
        color: #626262;
        padding-left: 1;
    }

    #bottom_bar {
        dock: bottom;
        height: 4;
        margin-bottom: 1;
    }

    #bottom_bar Footer {
        dock: none;
        width: 1fr;
        margin-top: 3;
        padding: 0 0;
    }

    .language_flag {
        width: 10;
        height: 4;
        padding: 0 1;
        margin-left: 1;
        border: round $border-blurred;
        border-subtitle-align: center;
        border-subtitle-color: #909090;
        opacity: 70%;
        &:hover { opacity: 100%; }
        &.-active {
            opacity: 100%;
            border: round $accent;
            border-subtitle-color: $accent;
            border-subtitle-style: bold;
        }
    }
    """

    def on_mount(self) -> None:
        self.register_theme(CHARM_THEME)
        self.theme = "charm"
        self.title = "TipToiDl"
        self.api = TipToiAPI()
        self.catalog_items: list[dict] = []
        self.visible_items: list[dict] = []
        self.set_language("de_DE")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Horizontal(id="title_bar"):
            yield Static("TipToi DL", id="title")
            yield Static("Ravensburger tiptoi audio file downloader", id="subtitle")
        search = SearchInput(
            placeholder="Filter by name or ID…",
            id="search_input",
        )
        search.border_title = "Search"
        yield search
        table = CatalogTable(id="catalog_table", cursor_type="row", zebra_stripes=True)
        table.border_title = "Catalog"
        yield table
        with Horizontal(id="status_bar"):
            yield Spinner("", id="spinner")
            yield Static("Download catalog", id="status_label")
            yield GradientProgress(total=100, show_eta=False, id="progress_bar")
        with Horizontal(id="bottom_bar"):
            yield Footer()
            for language in LanguageFlag.FLAGS:
                yield LanguageFlag(cast("languages", language))

    async def on_unmount(self) -> None:
        """Clean up the API client when the app closes."""
        await self.api.aclose()

    def set_language(self, language: languages) -> None:
        """Highlight the flag of the given language and reload the catalog in it."""
        if language == getattr(self, "language", None):
            return
        self.language = language
        for flag in self.query(LanguageFlag):
            flag.set_class(flag.language == language, "-active")
        self.run_worker(self.load_catalog(language), exclusive=True)

    def action_next_language(self) -> None:
        codes = list(LanguageFlag.FLAGS)
        next_code = codes[(codes.index(self.language) + 1) % len(codes)]
        self.set_language(cast("languages", next_code))

    async def load_catalog(self, language: languages = "de_DE") -> None:
        """Fetch data from the API and update progress as we go."""
        bar = self.query_one("#progress_bar", GradientProgress)
        label = self.query_one("#status_label", Static)
        table = self.query_one("#catalog_table", DataTable)

        spinner = self.query_one(Spinner)
        spinner.spin()
        label.update(f"Fetching {language} catalog…")
        bar.total = 100
        bar.progress = 0

        timer = self.set_interval(
            1 / 20, lambda: bar.advance(1) if bar.progress < 90 else None
        )

        try:
            catalog = await self.api.get_catalog(language)
        finally:
            timer.stop()

        if not catalog:
            logger.error("Catalog was empty")
            spinner.done(ok=False)
            label.update("Error downloading catalog")
            return

        bar.progress = 100
        spinner.done()
        label.update(
            f"{language} catalog loaded · {len(catalog.get('products', []))} products"
        )

        self.catalog_items = catalog.get("products", [])

        if not table.columns:
            table.add_columns("Name", "ID", "Categories", "Age", "Description")
            (
                self.col_name,
                self.col_id,
                self.col_categories,
                self.col_age,
                self.col_description,
            ) = table.columns.keys()
        else:
            # clear() keeps the widths of the previous catalog, so reset them
            for column in table.columns.values():
                column.content_width = cell_len(column.label.plain)
        self._apply_filter()

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

    def _row_cells(self, item: dict) -> tuple[str, str, str, str]:
        """Cells of all columns except the description."""
        return (
            item.get("name", ""),
            item.get("id", ""),
            ", ".join(item.get("categories", [])),
            self._get_age_range(item),
        )

    def _description_width(self) -> int:
        """Width left for the description so the table never scrolls horizontally."""
        table = self.query_one("#catalog_table", DataTable)
        labels = [column.label for column in table.columns.values()][:-1]
        rows = [self._row_cells(item) for item in self.catalog_items]
        used = sum(
            max(cell_len(str(cell)) for cell in (label, *column))
            + 2 * table.cell_padding
            for label, column in zip(labels, zip(*rows), strict=True)
        )
        # Always reserve room for the vertical scrollbar so the width is stable
        available = table.content_region.width - table.styles.scrollbar_size_vertical
        return max(10, available - used - 2 * table.cell_padding)

    def _populate_table(self, items: list[dict]) -> None:
        """Clear and refill the table with the given items."""
        self.visible_items = items
        table = self.query_one("#catalog_table", DataTable)
        description = table.columns[self.col_description]
        description.auto_width = False
        description.width = self._description_width()
        table.clear()
        for item in items:
            table.add_row(
                *self._row_cells(item),
                Text(
                    " ".join(item.get("description", "").split()), overflow="ellipsis"
                ),
            )
        table.sort(self.col_id, self.col_categories)
        table.border_subtitle = f"{len(items)} of {len(self.catalog_items)}"

    def fit_description_column(self) -> None:
        """Refill the table if a resize changed the space left for the description."""
        if not getattr(self, "catalog_items", None):
            return
        table = self.query_one("#catalog_table", DataTable)
        if table.columns[self.col_description].width == self._description_width():
            return
        row = table.cursor_row
        self._populate_table(self.visible_items)
        table.move_cursor(row=row)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the table as the user types in the search box."""
        if event.input.id != "search_input":
            return
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Show only catalog items matching the current search query."""
        if not self.catalog_items:
            return
        query = self.query_one("#search_input", Input).value.strip().lower()
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

    def _find_item(self, item_id: str) -> dict | None:
        return next(
            (i for i in self.catalog_items if str(i.get("id")) == str(item_id)), None
        )

    def show_details(self, item_id: str) -> None:
        item = self._find_item(item_id)
        if item is not None:
            self.push_screen(DetailScreen(item, self._get_age_range(item)))

    def download_item(self, item_id: str) -> None:
        item = self._find_item(item_id)
        if item is None:
            return
        game_files = item.get("gameFiles", [])
        if not game_files:
            return
        url = game_files[0]["url"]
        filename = game_files[0]["fileName"]
        self.run_worker(self._download_file(url, filename), exclusive=True)

    async def _download_file(self, url: str, filename: str) -> None:
        bar = self.query_one("#progress_bar", GradientProgress)
        label = self.query_one("#status_label", Static)

        disk = self.find_tiptoi_disk()
        path = (Path(disk) / filename if disk else Path.home() / filename).resolve()

        spinner = self.query_one(Spinner)
        spinner.spin()
        label.update(f"Downloading {path!s}…")
        bar.progress = 0

        def on_progress(downloaded: int, total: int) -> None:
            bar.total = total or None
            bar.progress = downloaded

        async with TipToiAPI() as api:
            await api.get_audiofile(url, str(path), on_progress=on_progress)
            spinner.done()
            label.update(f"Downloaded {path!s}")
            self.push_screen(InfoScreen(f"Downloaded {path!s}", title="Done"))

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
