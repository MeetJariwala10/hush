<div align="center">

<img src=".github/assets/logo.svg" width="96" alt="hush logo">

# hush

**A quiet, minimal terminal for macOS.**

One command gives zsh a calm prompt, suggestions as you type, fuzzy search and better defaults.

[![Platform](https://img.shields.io/badge/platform-macOS-5b9bd5?style=flat-square)](#install)
[![Shell](https://img.shields.io/badge/shell-zsh-8fbf72?style=flat-square)](config/hush.zsh)
[![Prompt](https://img.shields.io/badge/prompt-Starship-5b9bd5?style=flat-square)](config/starship.toml)
[![License](https://img.shields.io/badge/license-MIT-8fbf72?style=flat-square)](LICENSE)

[Features](#features) · [Install](#install) · [Customize](#customize) · [Uninstall](#uninstall)

</div>

## Features

### A prompt that stays quiet

Only the current folder is bright. Branch, changes, runtime and timing stay muted until you need them. The prompt never uses red: yellow marks anything that needs attention.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/prompt-dark.svg">
  <img src=".github/assets/prompt-light.svg" width="100%" alt="The parts of the hush prompt: accent bar, folder, git branch, git status, runtime, duration and clock">
</picture>

### Git at a glance

See what changed, what is staged and what is waiting to be pushed, without typing `git status`.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/git-dark.svg">
  <img src=".github/assets/git-light.svg" width="100%" alt="Git status in the hush prompt changing from modified and untracked, to staged, to one commit ahead">
</picture>

### Suggestions as you type

Gray hints come from your history. Press `→` to accept one. `Tab` opens a menu you can move through with the arrow keys.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/suggestions-dark.svg">
  <img src=".github/assets/suggestions-light.svg" width="100%" alt="A gray suggestion from history while typing a docker command, and the Tab completion menu for git">
</picture>

### Find any past command

`Ctrl R` searches your history as you type. `Ctrl T` finds files and `⌥ C` jumps into folders the same way.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/fuzzy-dark.svg">
  <img src=".github/assets/fuzzy-light.svg" width="100%" alt="Searching command history with Ctrl R: typing dock lists every docker command run before">
</picture>

### Jump to any project

`z` learns the folders you visit. Type part of a name to go straight there, from anywhere.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/jump-dark.svg">
  <img src=".github/assets/jump-light.svg" width="100%" alt="Jumping between projects with z: z api and z dot go straight to deep folders">
</picture>

### Readable files

`ls` shows icons with folders first. `cat` adds syntax highlighting and line numbers.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/files-dark.svg">
  <img src=".github/assets/files-light.svg" width="100%" alt="ls with file icons, and cat showing package.json with syntax highlighting and line numbers">
</picture>

Every shortcut and alias is in the [cheatsheet](docs/cheatsheet.md).

## Install

You need macOS and [Homebrew](https://brew.sh).

```sh
git clone https://github.com/MeetJariwala10/hush.git
cd hush
./install.sh
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/install-dark.svg">
  <img src=".github/assets/install-light.svg" width="100%" alt="Running ./install.sh turns the default zsh prompt into the hush prompt">
</picture>

Last step: set your terminal font to **JetBrainsMono Nerd Font**, which the installer added, then open a new tab.

| Terminal | Where to set the font |
| --- | --- |
| Terminal.app | Settings > Profiles > Text > Font |
| iTerm2 | Settings > Profiles > Text > Font |
| Ghostty | Add `font-family = JetBrainsMono Nerd Font` to its config |
| VS Code | Already set by the installer |

<details>
<summary>What the installer changes</summary>

<br>

1. Installs the packages in the [Brewfile](Brewfile), skipping any you already have.
2. Copies `config/` to `~/.config/hush/`.
3. Adds one `source` line to `~/.zshrc`, between `# >>> hush >>>` markers.
4. Sets the VS Code terminal font, if VS Code is installed.

Every file is backed up before it changes, as `<file>.bak-<date>`. Your existing `~/.config/starship.toml` is not modified, but hush uses its own copy while installed.

</details>

## What's inside

| Tool | Role |
| --- | --- |
| [Starship](https://starship.rs) | Prompt |
| [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) | Suggestions as you type |
| [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) | Colors commands as you type |
| [fzf](https://github.com/junegunn/fzf) | Fuzzy finder |
| [zoxide](https://github.com/ajeetdsouza/zoxide) | Smarter `cd` |
| [eza](https://github.com/eza-community/eza) | Modern `ls` |
| [bat](https://github.com/sharkdp/bat) | `cat` with syntax highlighting |
| [JetBrains Mono Nerd Font](https://www.nerdfonts.com) | Font with icons |

## Customize

Your config lives in `~/.config/hush/`. Edit `starship.toml` for the prompt or `hush.zsh` for the shell, then run `reload`.

See [docs/customize.md](docs/customize.md) for common changes, the git status icons and the color palette.

## Uninstall

```sh
./uninstall.sh
```

This removes the hush lines from `~/.zshrc` and deletes `~/.config/hush`. If you edited your config, it is kept as `~/.config/hush.bak-<date>` instead. The VS Code font setting and Homebrew packages stay; the script prints the command to remove the packages.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Icons show as boxes | Set your terminal font to JetBrainsMono Nerd Font. |
| `⌥ C` types `ç` | Terminal.app: Settings > Profiles > Keyboard > Use Option as Meta key. |
| Prompt has not changed | Open a new tab, or run `exec zsh`. |
| `command not found: brew` | Install [Homebrew](https://brew.sh), then run `./install.sh` again. |

## Contributing

Issues and pull requests are welcome. Please keep changes minimal and calm, and use no red.

The images in this README are generated by [`.github/assets/render.py`](.github/assets/render.py). Run it after changing the prompt so they stay accurate.

## Credits

hush configures the tools above and does not include their code; each keeps its own license.
The README images embed a subset of [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
([SIL OFL 1.1](.github/assets/OFL.txt)), reduced to the characters each image uses and patched by [Nerd Fonts](https://www.nerdfonts.com), with icons from
[Font Awesome](https://fontawesome.com) ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)) and
[Devicons](https://github.com/vorillaz/devicons) (MIT).

## License

[MIT](LICENSE)
