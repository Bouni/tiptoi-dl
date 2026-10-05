# VHS documentation
#
Output demo.gif
Set Shell "zsh"
Set FontSize 18
Set Height 700
Set Width 1300
Set Padding 10
Set Theme { "background": "#171717", "foreground": "#DDDDDD", "black": "#171717", "red": "#FF4672", "green": "#04B575", "yellow": "#FFB86C", "blue": "#7D56F4", "magenta": "#EE6FF8", "cyan": "#5A56E0", "white": "#DDDDDD", "brightBlack": "#626262", "brightRed": "#FF4672", "brightGreen": "#04B575", "brightYellow": "#FFB86C", "brightBlue": "#7D56F4", "brightMagenta": "#FF5FAF", "brightCyan": "#5A56E0", "brightWhite": "#FFFFFF", "cursor": "#FF5FAF", "selection": "#7D56F4" }
Set TypingSpeed 80ms
Set Framerate 10

Hide
Type "uv run tiptoi-dl"
Enter
Sleep 500ms
Show

# Catalog loads
Sleep 4s

# Filter the catalog
Type "Feuerwehr"
Sleep 1500ms

# Jump to the table and pick an entry
Tab
Sleep 500ms
Down
Sleep 400ms
Down
Sleep 400ms
Up
Sleep 800ms

# Download the selected file
Ctrl+d
Sleep 1500ms
Enter
Sleep 4s

# Close the "Done" dialog
Enter
Sleep 2s

Hide
Ctrl+q
Sleep 500ms
