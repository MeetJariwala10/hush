"""Render the README images (light and dark) for hush.

Each image is an SVG of a terminal window drawn on a grid, using hush's real
prompt colors. A subset of JetBrainsMono Nerd Font is embedded so the icons
show on GitHub.

    python3 -m venv .venv
    .venv/bin/pip install fonttools brotli
    .venv/bin/python .github/assets/render.py

Requires JetBrainsMono Nerd Font (brew install --cask font-jetbrains-mono-nerd-font).
Set HUSH_FONT_DIR if it is not in ~/Library/Fonts. The font's license is in OFL.txt.
"""

import base64
import io
import os
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent
FONT_DIR = Path(os.environ.get("HUSH_FONT_DIR", "~/Library/Fonts")).expanduser()

# Prompt palette, from config/starship.toml
BLUE, GREEN, YELLOW = "#5b9bd5", "#8fbf72", "#cbb486"
ACCENT, MUTED, DIM, SEP = "#61afef", "#6b7280", "#565d68", "#454b54"
# Terminal
TERM_BG, FG, OUTPUT, GHOST = "#1c1f24", "#c9ced6", "#8b929c", "#6b727f"
WHITE, SEL_BG = "#ffffff", "#2c313a"
# fzf, from config/hush.zsh
FZF_HL, FZF_GREEN, FZF_BORDER = "#61afef", "#98c379", "#4b86c5"

BRANCH, MOD, STAGED, UNTRACKED = "", "", "", ""
NODE, FOLDER, MARKDOWN, TS = "", "", "", ""
AHEAD = "⇡"

MODES = {
    "light": dict(bg1="#f7faf5", bg2="#e9f1e4", border="#dde6d7", glow=0.24,
                  shadow="#1d2a1a", shadow_op=0.22, win="#2c3138",
                  label="#4b5563", leader="#9ca3af"),
    "dark": dict(bg1="#141b21", bg2="#0d1117", border="#232b33", glow=0.10,
                 shadow="#000000", shadow_op=0.6, win="#353b44",
                 label="#9aa4af", leader="#4b545e"),
}

W = 900          # canvas width
PADX = 22        # terminal padding inside the window
TITLE_H = 36

FONT_NOTICE = """<!--
  Text is set in a subset of JetBrainsMono Nerd Font, embedded below and
  reduced to the characters this image uses.
  JetBrains Mono: Copyright 2020 The JetBrains Mono Project Authors
  (https://github.com/JetBrains/JetBrainsMono), SIL Open Font License 1.1
  (https://openfontlicense.org). Patched by Nerd Fonts (https://www.nerdfonts.com).
  Icons: Font Awesome (https://fontawesome.com), CC BY 4.0; Devicons
  (https://github.com/vorillaz/devicons), MIT; Powerline symbols, MIT.
-->"""


# Line builders. A line is a list of (text, color, options) segments.

def seg(text, color, **opts):
    return (text, color, opts)


def info(folder, branch=None, status=(), runtime=None, duration=None,
         time="Sun 22 Nov 09:41", cols=88):
    """The first prompt line, laid out exactly like starship.toml."""
    s = [seg("▌ ", BLUE, name="bar"), seg(folder, ACCENT, bold=True, name="folder")]
    if branch:
        s += [seg(" · ", SEP), seg(f"{BRANCH} {branch}", MUTED, name="branch")]
    if status:
        s.append(seg(" ·", SEP))
        s += [seg(f"  {icon} {n}", color, name="status") for icon, n, color in status]
    if runtime:
        s += [seg(" · ", SEP), seg(f"{NODE} {runtime}", GREEN, name="runtime")]
    s.append(seg(" ", DIM))
    right = [seg(f"{duration}", YELLOW, name="duration"), seg("  ", DIM)] if duration else []
    right += [seg(" ", DIM), seg(time, DIM, name="clock")]
    used = sum(len(t) for t, _, _ in s + right)
    return s + [seg("─" * (cols - used), DIM)] + right


def cmd(*parts, ok=True, cursor=None):
    """The second prompt line: accent bar, ❯, then typed text."""
    s = [seg("▌ ", GREEN), seg("❯", GREEN if ok else YELLOW, name="char"), seg(" ", FG)]
    s += list(parts)
    if cursor is not None:
        s.append(seg(cursor or " ", GHOST, cursor=True))
    return s


def C(t):  # a valid command, as zsh-syntax-highlighting colors it
    return seg(t, GREEN)


def A(t):  # an argument
    return seg(t, FG)


def Q(t):  # a quoted string
    return seg(t, YELLOW)


def out(t, color=OUTPUT, **o):
    return [seg(t, color, **o)]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# Rendering

SHAPES = set("▌─│┬┼┴╭╮╰╯")


def shape(c, x, cy, cw, lh, color, width):
    """Draw a box-drawing or block character as vector shapes on its cell."""
    top, bot, mx, r = cy - lh / 2, cy + lh / 2, x + cw / 2, cw / 2
    if c == "▌":
        return f'<rect x="{x:.1f}" y="{top:.1f}" width="{cw / 2:.1f}" height="{lh:.1f}" fill="{color}"/>'
    paths = {
        "─": f"M{x:.1f} {cy:.1f}H{x + width:.1f}",
        "│": f"M{mx:.1f} {top:.1f}V{bot:.1f}",
        "┬": f"M{x:.1f} {cy:.1f}H{x + cw:.1f}M{mx:.1f} {cy:.1f}V{bot:.1f}",
        "┼": f"M{x:.1f} {cy:.1f}H{x + cw:.1f}M{mx:.1f} {top:.1f}V{bot:.1f}",
        "┴": f"M{x:.1f} {cy:.1f}H{x + cw:.1f}M{mx:.1f} {top:.1f}V{cy:.1f}",
        "╭": f"M{x + cw:.1f} {cy:.1f}H{mx + r:.1f}A{r:.1f} {r:.1f} 0 0 0 {mx:.1f} {cy + r:.1f}V{bot:.1f}",
        "╮": f"M{x:.1f} {cy:.1f}H{mx - r:.1f}A{r:.1f} {r:.1f} 0 0 1 {mx:.1f} {cy + r:.1f}V{bot:.1f}",
        "╰": f"M{mx:.1f} {top:.1f}V{cy - r:.1f}A{r:.1f} {r:.1f} 0 0 0 {mx + r:.1f} {cy:.1f}H{x + cw:.1f}",
        "╯": f"M{mx:.1f} {top:.1f}V{cy - r:.1f}A{r:.1f} {r:.1f} 0 0 1 {mx - r:.1f} {cy:.1f}H{x:.1f}",
    }
    return f'<path d="{paths[c]}" stroke="{color}" stroke-width="1.1" fill="none"/>'


def render_lines(lines, x0, y0, fs, lh):
    """Draw lines on a character grid. Returns (svg, regular chars, bold chars, named spans)."""
    cw = fs * 0.6
    parts, regular, bold, names = [], set(), set(), {}
    for i, line in enumerate(lines):
        y = y0 + i * lh
        col = 0
        for text, color, o in line:
            x = x0 + col * cw
            if o.get("bg"):
                parts.append(f'<rect x="{x:.1f}" y="{y - fs * 0.95:.1f}" width="{len(text) * cw:.1f}" '
                             f'height="{lh:.1f}" fill="{o["bg"]}"/>')
            if o.get("cursor"):
                parts.append(f'<rect x="{x:.1f}" y="{y - fs * 0.92:.1f}" width="{cw:.1f}" '
                             f'height="{fs * 1.22:.1f}" rx="1" fill="{FG}"/>')
            if "name" in o:
                start = col + len(text) - len(text.lstrip())
                a, _, _ = names.get(o["name"], (start, start, i))
                names[o["name"]] = (min(a, start), col + len(text.rstrip()), i)
            (bold if o.get("bold") else regular).update(c for c in text if c not in SHAPES)
            weight = ' font-weight="700"' if o.get("bold") else ""
            k = 0
            while k < len(text):
                c = text[k]
                cx = x0 + (col + k) * cw
                if c == " ":
                    k += 1
                elif c in SHAPES:
                    # box and block characters fill the whole cell, as in a terminal
                    j = k
                    while c == "─" and j + 1 < len(text) and text[j + 1] == "─":
                        j += 1
                    parts.append(shape(c, cx, y - 0.36 * fs, cw, lh, color, (j - k + 1) * cw))
                    k = j + 1
                else:
                    j = k
                    while j < len(text) and text[j] != " " and text[j] not in SHAPES:
                        j += 1
                    start = k
                    if o.get("cursor") and k == 0:
                        # the character under the block cursor is drawn in the background color
                        parts.append(f'<text x="{cx:.1f}" y="{y:.1f}" fill="{TERM_BG}">{esc(c)}</text>')
                        start = k + 1
                    if start < j:
                        xs = " ".join(f"{x0 + (col + n) * cw:.1f}" for n in range(start, j))
                        parts.append(f'<text x="{xs}" y="{y:.1f}" fill="{color}"{weight}>{esc(text[start:j])}</text>')
                    k = j
            col += len(text)
    return "\n".join(parts), regular, bold, names


def font_face(name, chars, weight):
    font = TTFont(FONT_DIR / name, recalcTimestamp=False)  # same bytes on every run
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    opts.name_IDs = [0, 1, 2, 5, 13, 14]  # keep the copyright and OFL notice
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) or " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f'@font-face{{font-family:"hush-mono";font-weight:{weight};'
            f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')


def chips(keys, right_x, y, regular):
    """Keyboard hints drawn as key caps in the title bar."""
    parts, x = [], right_x
    for key in reversed(keys):
        w = max(22, len(key) * 6.6 + 14)
        x -= w
        parts.append(f'<rect x="{x:.1f}" y="{y - 11}" width="{w:.1f}" height="21" rx="5" '
                     f'fill="#262a30" stroke="#3d434c"/>'
                     f'<text x="{x + w / 2:.1f}" y="{y + 3.5:.1f}" text-anchor="middle" '
                     f'fill="#aeb5bf" style="font-size:11px">{esc(key)}</text>')
        regular.update(key)
        x -= 6
    return "".join(parts)


def scene(name, lines, alt, title="zsh", keys=(), fs=14, lh=22, cols=88,
          labels=None, top=44, bottom=48, chrome=True):
    cw = fs * 0.6
    title_h = TITLE_H if chrome else 0
    win_w = cols * cw + PADX * 2
    win_x = (W - win_w) / 2
    label_rows = 3 if labels else 0
    win_y = top + label_rows * 22 + (14 if labels else 0)
    body_y = win_y + title_h + 18 + fs * 0.8
    win_h = title_h + 18 + len(lines) * lh + 10
    below = 46 if labels and labels.get("below") else 0
    H = round(win_y + win_h + bottom + below)

    content, regular, bold, names = render_lines(lines, win_x + PADX, body_y, fs, lh)
    regular.update(title)
    chip_svg = chips(list(keys), win_x + win_w - 14, win_y + TITLE_H / 2, regular) if chrome else ""

    chrome_svg = (
        f'<circle cx="{win_x + 20:.1f}" cy="{win_y + 18}" r="6" fill="#3a3f47"/>'
        f'<circle cx="{win_x + 40:.1f}" cy="{win_y + 18}" r="6" fill="#3a3f47"/>'
        f'<circle cx="{win_x + 60:.1f}" cy="{win_y + 18}" r="6" fill="#3a3f47"/>'
        f'<text x="{W / 2}" y="{win_y + 22.5:.1f}" text-anchor="middle" fill="{MUTED}" style="font-size:12px">{esc(title)}</text>'
        f'<line x1="{win_x + 1:.1f}" y1="{win_y + TITLE_H + 0.5:.1f}" x2="{win_x + win_w - 1:.1f}" '
        f'y2="{win_y + TITLE_H + 0.5:.1f}" stroke="#2a2f36"/>'
    ) if chrome else ""

    for mode, m in MODES.items():
        ann = []
        if labels:
            ann.append(annotate(labels, names, win_x + PADX, body_y, fs, lh, cw,
                                win_y, win_y + win_h, m, regular))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(alt)}">
{FONT_NOTICE}
<defs>
<style>
{font_face("JetBrainsMonoNerdFont-Regular.ttf", regular, 400)}
{font_face("JetBrainsMonoNerdFont-Bold.ttf", bold or {" "}, 700)}
text{{font-family:"hush-mono",ui-monospace,Menlo,monospace;font-size:{fs}px}}
</style>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{m["bg1"]}"/><stop offset="1" stop-color="{m["bg2"]}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{GREEN}" stop-opacity="{m["glow"]}"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<filter id="shadow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="{m["shadow"]}" flood-opacity="{m["shadow_op"]}"/></filter>
</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#bg)" stroke="{m["border"]}"/>
<ellipse cx="{W / 2}" cy="{win_y + win_h * 0.55:.1f}" rx="{win_w * 0.62:.1f}" ry="{win_h * 0.75:.1f}" fill="url(#glow)"/>
<g filter="url(#shadow)"><rect x="{win_x:.1f}" y="{win_y:.1f}" width="{win_w:.1f}" height="{win_h:.1f}" rx="11" fill="{TERM_BG}" stroke="{m["win"]}"/></g>
{chrome_svg}
{chip_svg}
{content}
{"".join(ann)}
</svg>
'''
        path = OUT / f"{name}-{mode}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"{path.name:24} {W}x{H}  {len(svg) // 1024} KB")


def annotate(labels, names, x0, y0, fs, lh, cw, win_top, win_bottom, m, regular):
    """Labels above the window with leader lines down to each prompt segment."""
    lfs, row_h = 11.5, 22
    parts, placed = [], []  # placed: (row, x1, x2, leader_x)
    for key, text in labels["above"]:
        a, b, line = names[key]
        lx = x0 + (a + b) / 2 * cw
        if key == "bar":
            lx = x0 + 0.35 * cw
        w = len(text) * lfs * 0.6
        anchor = "end" if key == "bar" else "middle"
        x1 = lx - w - 8 if anchor == "end" else lx - w / 2
        x2 = lx + 2 if anchor == "end" else x1 + w
        for row in range(3):
            clash = any(r == row and not (x2 + 10 < p1 or x1 > p2 + 10) for r, p1, p2, _ in placed)
            crosses = any(r < row and p1 - 4 < lx < p2 + 4 for r, p1, p2, _ in placed)
            covers = any(r > row and x1 - 4 < plx < x2 + 4 for r, _, _, plx in placed)
            if not (clash or crosses or covers):
                break
        placed.append((row, x1, x2, lx))
        ty = win_top - 14 - row * row_h
        tip = y0 + line * lh - fs * 0.95
        parts.append(f'<line x1="{lx:.1f}" y1="{ty + 5:.1f}" x2="{lx:.1f}" y2="{tip:.1f}" '
                     f'stroke="{m["leader"]}" stroke-width="1"/>'
                     f'<circle cx="{lx:.1f}" cy="{tip:.1f}" r="2.2" fill="{m["leader"]}"/>'
                     f'<text x="{lx if anchor == "middle" else lx - 6:.1f}" y="{ty:.1f}" text-anchor="{anchor}" '
                     f'fill="{m["label"]}" style="font-size:{lfs}px">{esc(text)}</text>')
        regular.update(text)
    for key, text in labels.get("below", []):
        a, b, line = names[key]
        lx = x0 + (a + b) / 2 * cw
        start = y0 + line * lh + fs * 0.4
        ty = win_bottom + 28
        parts.append(f'<circle cx="{lx:.1f}" cy="{start:.1f}" r="2.2" fill="{m["leader"]}"/>'
                     f'<line x1="{lx:.1f}" y1="{start:.1f}" x2="{lx:.1f}" y2="{ty - 13:.1f}" '
                     f'stroke="{m["leader"]}" stroke-width="1"/>'
                     f'<text x="{lx - 2:.1f}" y="{ty:.1f}" fill="{m["label"]}" style="font-size:{lfs}px">{esc(text)}</text>')
        regular.update(text)
    return "".join(parts)


# Scenes

def main():
    if not (FONT_DIR / "JetBrainsMonoNerdFont-Regular.ttf").exists():
        sys.exit(f"JetBrainsMono Nerd Font not found in {FONT_DIR}. "
                 "Install it, or set HUSH_FONT_DIR to its folder.")
    T = "Sun 22 Nov "
    api = dict(branch="main", runtime="v22.11.0")

    scene("prompt", [
        info("api", status=[(MOD, 2, YELLOW), (STAGED, 1, GREEN)], duration="12s",
             time=T + "09:42", cols=74, **api),
        cmd(cursor=""),
    ], "The parts of the hush prompt: accent bar, folder, git branch, git status, runtime, duration and clock",
        fs=16, lh=26, cols=74, top=34, bottom=30, chrome=False, labels={
            "above": [("bar", "accent bar"), ("folder", "folder"), ("branch", "git branch"),
                      ("status", "git status"), ("runtime", "runtime"), ("duration", "duration"),
                      ("clock", "clock")],
            "below": [("char", "green after success, yellow after an error")],
        })

    feat = dict(branch="feat/rate-limit", runtime="v22.11.0")
    scene("git", [
        info("api", status=[(MOD, 3, YELLOW), (UNTRACKED, 1, BLUE)], time=T + "09:43", **feat),
        cmd(C("git"), A(" add .")),
        [],
        info("api", status=[(STAGED, 4, GREEN)], time=T + "09:43", **feat),
        cmd(C("git"), A(" commit -m "), Q('"Add rate limiting"')),
        out("[feat/rate-limit 3f2a1c9] Add rate limiting"),
        out(" 4 files changed, 86 insertions(+), 3 deletions(-)"),
        [],
        info("api", status=[(AHEAD, 1, GREEN)], time=T + "09:44", **feat),
        cmd(C("git"), A(" push"), cursor=""),
    ], "Git status in the hush prompt changing from modified and untracked, to staged, to one commit ahead",
        title="~/work/api")

    scene("suggestions", [
        info("api", time=T + "09:45", **api),
        cmd(C("docker"), A(" compose u"), cursor="p -d --build"),
        [],
        info("api", time=T + "09:46", **api),
        cmd(C("git"), A(" rebase"), cursor=""),
        out("── main porcelain command ──", BLUE),
        [seg("rebase   ", WHITE, bg=SEL_BG), seg("-- reapply commits on top of another base tip", WHITE, bg=SEL_BG)],
        [seg("reset    ", FG), seg("-- reset current HEAD to the specified state", OUTPUT)],
        [seg("restore  ", FG), seg("-- restore working tree files", OUTPUT)],
        [seg("revert   ", FG), seg("-- revert existing commits", OUTPUT)],
    ], "A gray suggestion from history while typing a docker command, and the Tab completion menu for git",
        title="~/work/api", keys=["→", "tab"])

    box_w = 88
    def boxed(parts, row_bg=None):
        used = sum(len(t) for t, _, _ in parts)
        fill = [seg(" " * (box_w - 4 - used), FG, **({"bg": row_bg} if row_bg else {}))]
        return [seg("│ ", FZF_BORDER)] + parts + fill + [seg(" │", FZF_BORDER)]

    def hist(num, rest, selected=False):
        bg = {"bg": SEL_BG} if selected else {}
        fg = WHITE if selected else FG
        return boxed([seg("▌ " if selected else "  ", FZF_GREEN, **bg), seg(f"{num}  ", OUTPUT, **bg),
                      seg("dock", FZF_HL, **bg), seg(rest, fg, **bg)], SEL_BG if selected else None)

    scene("fuzzy", [
        info("api", time=T + "09:47", **api),
        cmd(cursor=""),
        out("╭" + "─" * (box_w - 2) + "╮", FZF_BORDER),
        boxed([seg("> ", FZF_HL), seg("dock", FG), seg("  < 5/2841", FZF_GREEN)]),
        hist(2194, "er compose up -d --build", selected=True),
        hist(2101, "er compose logs -f api"),
        hist(1988, "er build -t api ."),
        hist(1720, "er exec -it api sh"),
        hist(1533, "er system prune -af"),
        out("╰" + "─" * (box_w - 2) + "╯", FZF_BORDER),
    ], "Searching command history with Ctrl R: typing dock lists every docker command run before",
        title="~/work/api", keys=["ctrl", "R"])

    note = lambda t: seg(t, DIM)
    scene("jump", [
        info("~", time=T + "09:40"),
        cmd(C("z"), A(" api"), note("        # ~/work/acme/services/api")),
        [],
        info("api", time=T + "09:40", **api),
        cmd(C("z"), A(" dot"), note("        # ~/code/dotfiles")),
        [],
        info("dotfiles", branch="main", time=T + "09:41"),
        cmd(C("z"), A(" -"), note("          # back to api"), cursor=""),
    ], "Jumping between projects with z: z api and z dot go straight to deep folders",
        title="zsh")

    grid = "─" * 7
    def bat(n, *parts):
        return [seg(f"{n:>4}   ", DIM), seg("│ ", SEP)] + list(parts)
    K = lambda t: seg(t, BLUE)
    S = lambda t: seg(t, GREEN)
    P = lambda t: seg(t, FG)
    scene("files", [
        info("api", time=T + "09:48", **api),
        cmd(C("ls")),
        [seg(f"{FOLDER} src", BLUE, bold=True), seg("   ", FG), seg(f"{FOLDER} tests", BLUE, bold=True),
         seg("   ", FG), seg(f"{NODE} package.json", FG), seg("   ", FG),
         seg(f"{MARKDOWN} README.md", FG), seg("   ", FG), seg(f"{TS} tsconfig.json", FG)],
        [],
        info("api", time=T + "09:48", **api),
        cmd(C("cat"), A(" package.json")),
        out(grid + "┬" + "─" * 80, SEP),
        [seg("       ", FG), seg("│ ", SEP), seg("File: ", FG), seg("package.json", FG, bold=True)],
        out(grid + "┼" + "─" * 80, SEP),
        bat(1, P("{")),
        bat(2, P("  "), K('"name"'), P(": "), S('"api"'), P(",")),
        bat(3, P("  "), K('"version"'), P(": "), S('"1.4.0"'), P(",")),
        bat(4, P("  "), K('"scripts"'), P(": { "), K('"test"'), P(": "), S('"vitest"'), P(" }")),
        bat(5, P("}")),
        out(grid + "┴" + "─" * 80, SEP),
    ], "ls with file icons, and cat showing package.json with syntax highlighting and line numbers",
        title="~/work/api")

    scene("install", [
        [seg("you@mac hush % ./install.sh", FG)],
        [seg("==> ", BLUE), seg("Installing packages", WHITE, bold=True)],
        [seg("    ✓ ", GREEN), seg("Packages ready", FG)],
        [seg("==> ", BLUE), seg("Copying config to ~/.config/hush", WHITE, bold=True)],
        [seg("    ✓ ", GREEN), seg("Config copied", FG)],
        [seg("==> ", BLUE), seg("Loading hush from .zshrc", WHITE, bold=True)],
        [seg("    ✓ ", GREEN), seg("Added to .zshrc", FG)],
        [seg("you@mac hush % exec zsh", FG)],
        [],
        info("hush", branch="main", time=T + "09:31"),
        cmd(cursor=""),
    ], "Running ./install.sh turns the default zsh prompt into the hush prompt",
        title="zsh")


if __name__ == "__main__":
    main()
