# Cheatsheet

Everything hush adds to your shell.

## Keyboard

| Keys | Action |
| --- | --- |
| `→` or `End` | Accept the suggestion |
| `⌥ →` | Accept the next word of the suggestion |
| `↑` `↓` | Search history for what you have typed so far |
| `Tab` | Open the completion menu, then move with arrow keys |
| `Ctrl R` | Search command history |
| `Ctrl T` | Insert a file path, with a preview |
| `⌥ C` | Jump into a subfolder, with a preview |

`⌥ C` needs the Option key to act as Meta. In Terminal.app, turn on
**Settings > Profiles > Keyboard > Use Option as Meta key**.

## Files

| Command | Action |
| --- | --- |
| `ls` | List files with icons, folders first |
| `ll` | Long list with size, date and git status |
| `la` | Long list including hidden files |
| `lt` | Tree view, two levels deep |
| `cat <file>` | Print a file with syntax highlighting |
| `bat <file>` | Same, with paging for long files |

## Moving around

| Command | Action |
| --- | --- |
| `z <name>` | Jump to a folder you have visited, e.g. `z dash` |
| `z <a> <b>` | Jump to a folder matching both words |
| `zi` | Pick from visited folders |
| `z -` | Go back to the previous folder |
| `<folder>` | Type a folder name to `cd` into it |
| `..` `...` | Go up one or two levels |
| `dirs -v` | Show recent folders, then `cd -2` to jump back |

`z` learns as you go. Use `cd` normally for a while and it will know your projects.

## Fuzzy completion

| Usage | Action |
| --- | --- |
| `<cmd> **<Tab>` | Fuzzy-complete a path, e.g. `code **<Tab>` |
| `kill -9 <Tab>` | Pick a process |

In the picker, type to filter, use arrows to move, `Enter` to select and `Esc` to cancel.

## History

- Keeps at least 50,000 commands, without duplicates. A larger limit you already set is kept.
- Shared live across all open tabs.
- Start a command with a space to keep it out of history.

## Maintenance

| Command | Action |
| --- | --- |
| `reload` | Restart the shell to apply config changes |
| `starship print-config` | Check the prompt config for errors |
| `brew upgrade` | Update all tools |
