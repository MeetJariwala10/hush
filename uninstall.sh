#!/usr/bin/env bash
#
# Removes hush from your shell. Homebrew packages stay installed.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUSH_HOME="$HOME/.config/hush"
ZSHRC="${ZDOTDIR:-$HOME}/.zshrc"
STAMP="$(date +%Y%m%d-%H%M%S)"
BEGIN="# >>> hush >>>"
END="# <<< hush <<<"

ok()   { printf '\033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '\033[33m!\033[0m %s\n' "$1"; }

# Remove the hush block from .zshrc, only when both markers are intact.
if [[ -f "$ZSHRC" ]] && grep -qF "$BEGIN" "$ZSHRC"; then
  if grep -qxF "$BEGIN" "$ZSHRC" && grep -qxF "$END" "$ZSHRC"; then
    cp "$ZSHRC" "$ZSHRC.bak-$STAMP"
    tmp="$(mktemp)"
    awk -v b="$BEGIN" -v e="$END" '$0 == b { skip = 1; next } skip && $0 == e { skip = 0; next } !skip' \
      "$ZSHRC" > "$tmp"
    cat "$tmp" > "$ZSHRC"  # write in place, so a symlinked .zshrc stays a symlink
    rm -f "$tmp"
    ok "Removed hush from .zshrc (backup: .zshrc.bak-$STAMP)"
  else
    warn "The hush markers in .zshrc were edited, so it was left unchanged."
    warn "Delete the lines between '$BEGIN' and '$END' yourself."
  fi
fi

# Remove the config. Keep it instead if you changed anything in it.
if [[ -d "$HUSH_HOME" ]]; then
  if diff -rq "$REPO/config" "$HUSH_HOME" >/dev/null 2>&1; then
    rm -rf "$HUSH_HOME"
    ok "Removed ~/.config/hush"
  else
    mv "$HUSH_HOME" "$HUSH_HOME.bak-$STAMP"
    ok "Kept your edited config as ~/.config/hush.bak-$STAMP"
  fi
fi

cat <<'EOF'

hush is uninstalled. Open a new tab to get your previous prompt back.

Left in place: the VS Code terminal font setting, and the Homebrew packages.
To remove packages you no longer use:
  brew uninstall starship zsh-autosuggestions zsh-syntax-highlighting fzf zoxide eza bat
  brew uninstall --cask font-jetbrains-mono-nerd-font
EOF
