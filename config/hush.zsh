# hush · zsh configuration
# https://github.com/MeetJariwala10/hush
#
# Loaded from ~/.zshrc by install.sh. Remove it with uninstall.sh.
# Each tool is optional: if one is missing, that part is skipped.

# Homebrew lives in /opt/homebrew on Apple silicon and /usr/local on Intel.
_hush_brew=${HOMEBREW_PREFIX:-/opt/homebrew}
[[ -d $_hush_brew ]] || _hush_brew=/usr/local

# History: keep at least 50,000 commands (a larger existing limit is kept)
: ${HISTFILE:=~/.zsh_history}
(( HISTSIZE < 50000 )) && HISTSIZE=50000
(( SAVEHIST < 50000 )) && SAVEHIST=50000
setopt SHARE_HISTORY          # share history across open tabs
setopt INC_APPEND_HISTORY     # save each command as soon as it runs
setopt HIST_IGNORE_ALL_DUPS   # keep only the latest copy of a command
setopt HIST_IGNORE_SPACE      # commands typed with a leading space are not saved
setopt HIST_REDUCE_BLANKS
setopt HIST_VERIFY            # show !! expansions before running them

# Navigation
setopt AUTO_CD                # type a folder name to cd into it
setopt AUTO_PUSHD             # keep a directory stack, see `dirs -v`
setopt PUSHD_IGNORE_DUPS
setopt INTERACTIVE_COMMENTS

# Completion: case-insensitive, with a menu you can move through with arrow keys
fpath+=$_hush_brew/share/zsh/site-functions
autoload -Uz compinit && compinit
zmodload zsh/complist
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%F{blue}── %d ──%f'
zstyle ':completion:*:warnings' format '%F{yellow}no matches%f'

# Up and Down search history for what you have already typed
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search

# Prompt
if (( $+commands[starship] )); then
  export STARSHIP_CONFIG="$HOME/.config/hush/starship.toml"
  eval "$(starship init zsh)"
fi

# z <name> jumps to a frequent folder, zi picks one
(( $+commands[zoxide] )) && eval "$(zoxide init zsh)"

# Ctrl-R history, Ctrl-T files, Alt-C folders (needs fzf 0.48 or newer)
if (( $+commands[fzf] )); then
  eval "$(fzf --zsh 2>/dev/null)"
  export FZF_DEFAULT_OPTS="
    --height 45% --layout=reverse --border=rounded --info=inline
    --color=fg:-1,bg:-1,hl:#61afef,fg+:#ffffff,bg+:#2c313a,hl+:#61afef
    --color=info:#98c379,prompt:#61afef,pointer:#98c379,marker:#98c379
    --color=spinner:#56b6c2,header:#56b6c2,border:#4b86c5,gutter:-1"
  export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 {} 2>/dev/null || eza --tree --color=always {} 2>/dev/null'"
  export FZF_ALT_C_OPTS="--preview 'eza --tree --level=2 --color=always --icons=always {}'"
fi

# Better defaults for everyday commands
if (( $+commands[eza] )); then
  alias ls='eza --group-directories-first --icons=auto'
  alias ll='eza -lh --group-directories-first --icons=auto --git'
  alias la='eza -lah --group-directories-first --icons=auto --git'
  alias lt='eza --tree --level=2 --icons=auto'
fi
if (( $+commands[bat] )); then
  alias cat='bat --paging=never'
  export BAT_THEME="ansi"
fi
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias reload='exec zsh'

# Suggestions as you type. Accept with Right arrow or End.
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#6b727f'
[[ -r $_hush_brew/share/zsh-autosuggestions/zsh-autosuggestions.zsh ]] &&
  source $_hush_brew/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# Syntax highlighting must be loaded last. Unknown commands are yellow, not red.
if [[ -r $_hush_brew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source $_hush_brew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=yellow,bold'
fi

unset _hush_brew
