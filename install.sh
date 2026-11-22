#!/usr/bin/env bash
#
# hush installer for macOS. Safe to run more than once.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUSH_HOME="$HOME/.config/hush"
ZSHRC="${ZDOTDIR:-$HOME}/.zshrc"
STAMP="$(date +%Y%m%d-%H%M%S)"
BEGIN="# >>> hush >>>"
END="# <<< hush <<<"

step() { printf '\n\033[34m==>\033[0m \033[1m%s\033[0m\n' "$1"; }
ok()   { printf '    \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '    \033[33m!\033[0m %s\n' "$1"; }
die()  { printf '\033[33merror:\033[0m %s\n' "$1" >&2; exit 1; }

[[ "$(uname -s)" == "Darwin" ]] || die "hush is built for macOS."
command -v brew >/dev/null 2>&1 || die "Homebrew is required. Install it from https://brew.sh and run this again."

step "Installing packages"
brew bundle install --no-upgrade --file="$REPO/Brewfile"
# hush needs fzf 0.48 or newer; upgrade only if the installed one is older
fzf --zsh >/dev/null 2>&1 || brew upgrade fzf
ok "Packages ready"

step "Copying config to ~/.config/hush"
mkdir -p "$HUSH_HOME"
for file in hush.zsh starship.toml; do
  dest="$HUSH_HOME/$file"
  if [[ -f "$dest" ]] && ! cmp -s "$REPO/config/$file" "$dest"; then
    cp "$dest" "$dest.bak-$STAMP"
    warn "Your edited $file was saved as $file.bak-$STAMP"
  fi
  cp "$REPO/config/$file" "$dest"
done
ok "Config copied"

step "Loading hush from .zshrc"
touch "$ZSHRC"
if grep -qF "$BEGIN" "$ZSHRC"; then
  ok "Already loaded"
else
  [[ -s "$ZSHRC" ]] && cp "$ZSHRC" "$ZSHRC.bak-$STAMP"
  printf '\n%s\n[[ -f "$HOME/.config/hush/hush.zsh" ]] && source "$HOME/.config/hush/hush.zsh"\n%s\n' \
    "$BEGIN" "$END" >> "$ZSHRC"
  ok "Added to .zshrc"
fi
if grep -q '^[^#]*starship init' "$ZSHRC"; then
  warn "Your .zshrc already runs 'starship init'. hush does this for you, so you can remove that line."
fi

vscode="$HOME/Library/Application Support/Code/User/settings.json"
if [[ -f "$vscode" ]]; then
  step "Setting the VS Code terminal font"
  status=0
  python3 - "$vscode" "$STAMP" <<'PY' || status=$?
import json, shutil, sys

path, stamp = sys.argv[1], sys.argv[2]
key = "terminal.integrated.fontFamily"
try:
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
except ValueError:
    sys.exit(1)  # comments or trailing commas: leave the file alone
if not isinstance(settings, dict):
    sys.exit(1)
if "Nerd Font" in str(settings.get(key, "")):
    sys.exit(3)  # already set
shutil.copy(path, f"{path}.bak-{stamp}")
settings[key] = "JetBrainsMono Nerd Font, Menlo, monospace"
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)
    f.write("\n")
PY
  case $status in
    0) ok "VS Code terminal font set" ;;
    3) ok "VS Code already uses a Nerd Font" ;;
    *) warn "Could not edit VS Code settings. Set terminal.integrated.fontFamily to \"JetBrainsMono Nerd Font\" yourself." ;;
  esac
fi

step "Almost done"
cat <<'EOF'
    Set your terminal font to "JetBrainsMono Nerd Font":

      Terminal.app   Settings > Profiles > Text > Font
      iTerm2         Settings > Profiles > Text > Font
      Ghostty        font-family = JetBrainsMono Nerd Font

    Then open a new tab, or run: exec zsh
EOF
