# Customize

hush installs two files to `~/.config/hush/`:

| File | Controls |
| --- | --- |
| `starship.toml` | The prompt |
| `hush.zsh` | History, completion, tools and aliases |

Edit either one, then run `reload`. If you run `install.sh` again, it replaces them
and keeps your edited copy as `<file>.bak-<date>`.

## The prompt

```text
▌ folder · branch · git status · runtime ──────────── duration  clock
▌ ❯
```

| Part | Shows |
| --- | --- |
| Accent bar | Blue on the info line, green on the input line |
| Folder | The current folder, the one bright element |
| Branch | The current git branch |
| Git status | One icon and count per change type, see below |
| Runtime | Node, Python, Go, Rust, Java, Ruby, PHP, Lua or Docker, when the project uses it |
| Duration | How long the last command took, when longer than 2 seconds |
| Clock | Day, date and time |
| `❯` | Green after success, yellow after an error |

## Git status

| Icon | Meaning | Color |
| --- | --- | --- |
| Pencil | Modified, not staged | Yellow |
| Check | Staged | Green |
| Question mark | Untracked | Blue |
| Archive | Stashed | Purple |
| Arrow | Renamed | Blue |
| Trash can | Deleted | Yellow |
| Warning | Merge conflict | Yellow |
| `⇡` `⇣` | Ahead of or behind the remote | Green, yellow |

Yellow means "needs attention". The prompt never uses red, and unknown commands you type are highlighted in yellow instead of the usual red.

## Colors

All prompt colors are set once in `[palettes.hush]` in `starship.toml`.

| Name | Hex | Used for |
| --- | --- | --- |
| `accent` | `#61afef` | Current folder |
| `blue` | `#5b9bd5` | Top accent bar, untracked, renamed |
| `green` | `#8fbf72` | Bottom accent bar, `❯`, staged, ahead |
| `yellow` | `#cbb486` | Modified, deleted, conflicts, behind, durations, errors, Rust |
| `muted` | `#6b7280` | Git branch |
| `dim` | `#565d68` | Fill line, clock |
| `sep` | `#454b54` | `·` separators |
| `teal` | `#56b6c2` | Go, Lua |
| `purple` | `#c678dd` | Stashed, Java, Ruby |

## Common changes

All of these go in `~/.config/hush/starship.toml`.

| Change | How |
| --- | --- |
| One-line prompt | Remove `$line_break\` and `[▌ ](green)` from `format` |
| 12-hour clock | `time_format = '%I:%M %p'` under `[time]` |
| Hide the clock | `disabled = true` under `[time]` |
| Blank gap instead of a line | `symbol = ' '` under `[fill]` |
| Show more of the path | Raise `truncation_length` under `[directory]` |
| Different prompt symbol | Change `❯` under `[character]` |
| Different icons | Pick one from the [Nerd Fonts cheat sheet](https://www.nerdfonts.com/cheat-sheet) and replace the `symbol` |

See the [Starship docs](https://starship.rs/config/) for every option.

## Fonts

Any [Nerd Font](https://www.nerdfonts.com/font-downloads) works. To use another one:

```sh
brew install --cask font-fira-code-nerd-font
```

Then select it in your terminal settings.
