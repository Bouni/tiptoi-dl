# TipToi-dl

A linux CLI TipToi audiofile downloader.

## Motivation

[Ravensburger](https://www.ravensburger.de/), the manufacturer of the famous [TipToi](https://www.ravensburger.de/de-DE/entdecken/tiptoi) offers a Windows and a Mac Program for downloading new audiofiles.
As a Linux user you have to do that [manually via their website](https://service.ravensburger.de/tiptoi%C2%AE/tiptoi%C2%AE_Audiodateien) which is not the best experience.

So I decided to build this little CLI that allows me to download and copy the audiofile for a new book onto my kids TipToi within seconds.

## Setup

tiptoi-dl requires Python 3.11 or newer.

### Using uv (recommended)

uv brings its own Python, so this works regardless of your distro's Python version.

1. Install uv if you have not already (see https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv tool install tiptoi-dl` (or `uv tool install git+https://github.com/Bouni/tiptoi-dl.git` for the main branch)
3. Run the app: `tiptoi-dl`

> [!NOTE]
> If the command is not found, the path is most likely not in your PATH.
> run `uv tool update-shell` to fix that

### Using pipx

pipx is packaged by most distros, e.g. `sudo apt install pipx`, `sudo dnf install pipx` or `sudo pacman -S python-pipx`.

1. Run `pipx install tiptoi-dl`
2. Run the app: `tiptoi-dl`

> [!NOTE]
> If the command is not found, run `pipx ensurepath` and open a new terminal.

## Usage

On start, tiptoi-dl loads the full catalog and shows it in a table.

| Key | Action |
| --- | --- |
| type in the search bar | filter the catalog by name or product ID |
| `Tab` | jump from the search bar to the table |
| `↑` / `↓` | select an entry |
| `Enter` | show details of the selected entry |
| `Ctrl+D` | download the `.gme` file of the selected entry |
| `Ctrl+Q` | quit |

If a TipToi pen is connected via USB and mounted, the `.gme` file is saved directly onto it.
Otherwise it is saved into the current directory.

![](https://raw.githubusercontent.com/Bouni/tiptoi-dl/main/demo.gif)

## Disclaimer

tiptoi-dl is neither offered nor supported by Ravensburger.
The authors do not take any liability for possible damages.
